from mistralai import Mistral
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from fastapi import status
from econome.settings import settings
import os
import fal_client
from econome.db import get_econome_db
from econome.exceptions import DocumentNotFoundError
from bson import ObjectId
from typing import Annotated
from pymongo.database import Database
import logging


logging.basicConfig(level="DEBUG")
logger = logging.getLogger("econome")


client = Mistral(api_key=settings.mistral_key)
router = APIRouter(prefix="/recipes")
econome_db = get_econome_db()


def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            logger.info(log["message"])


class Ingredient(BaseModel):
    name: str
    quantity: str | None

    def __str__(self):
        return f"{self.quantity} of {self.name}"


class Ingredients(BaseModel):
    ingredients: list[Ingredient]


class RecipeStep(BaseModel):
    content: str


class Recipe(BaseModel):
    meal: str
    steps: list[RecipeStep]
    image_url: str | None

    @classmethod
    def from_db_recipe(cls, db_recipe) -> "Recipe":
        recipe = cls(
            meal=db_recipe["meal"],
            steps=[RecipeStep(**step) for step in db_recipe["steps"]],
            image_url=db_recipe["image_url"],
        )
        return recipe


class SavedRecipe(BaseModel):
    id: str


class DeletedRecipe(BaseModel):
    id: str


def _generate_recipe(ingredients: list[Ingredient]) -> Recipe:
    ingredients_formatted = ",".join((str(ingredient) for ingredient in ingredients))
    chat_response = client.chat.parse(
        model=settings.mistral_model,
        messages=[
            {
                "role": "user",
                "content": f"Generate a recipe that has (not exclusively) the following ingredients: {ingredients_formatted}",
            },
        ],
        response_format=Recipe,
    )
    parsed_response = chat_response.choices[0].message.parsed
    if os.environ.get("FAL_KEY"):
        handler = fal_client.submit(
            settings.flux_model, arguments={"prompt": parsed_response.meal}
        )
        result = fal_client.result(settings.flux_model, handler.request_id)
        if result.get("images"):
            parsed_response.image_url = result["images"][0]["url"]
    return parsed_response


@router.post("/", response_model=Recipe, status_code=status.HTTP_200_OK)
async def generate_recipe_from_txt(ingredients: List[Ingredient]) -> Recipe:
    recipe = _generate_recipe(ingredients)
    return recipe


@router.post("/vision", response_model=Recipe, status_code=status.HTTP_200_OK)
async def generate_recipe_from_img(image_url: str) -> Recipe:
    chat_response = client.chat.parse(
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What ingredients are in this image alongside their quantity?",
                    },
                    {"type": "image_url", "image_url": image_url},
                ],
            }
        ],
        response_format=List[Ingredient],
    )
    recipe = _generate_recipe(chat_response.choices[0].message.parsed)
    return recipe


@router.post("/save", status_code=status.HTTP_201_CREATED, response_model=SavedRecipe)
async def save_recipe(
    recipe: Recipe, econome_db: Annotated[Database, Depends(get_econome_db)]
):
    saved_recipe = econome_db.recipes.insert_one(recipe.model_dump())
    logger.info("Saved new recipe", dict(id=saved_recipe.inserted_id))
    return SavedRecipe(id=str(saved_recipe.inserted_id))


@router.delete(
    "/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=DeletedRecipe
)
async def delete_recipe(
    id: str, econome_db: Annotated[Database, Depends(get_econome_db)]
):
    result = econome_db.recipes.delete_one({"_id": ObjectId(id)})
    if not result.deleted_count:
        raise DocumentNotFoundError()
    logger.info("Deleted recipe", dict(id=id))
    return DeletedRecipe(id=id)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[Recipe])
async def get_recipes(econome_db: Annotated[Database, Depends(get_econome_db)]):
    recipes = econome_db.recipes.find()
    recipes = [Recipe.from_db_recipe(recipe) for recipe in recipes]
    return recipes


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=List[Recipe])
async def get_recipe(id: str, econome_db: Annotated[Database, Depends(get_econome_db)]):
    recipe = econome_db.recipes.find_one({"_id": ObjectId(id)})
    if not recipe:
        raise DocumentNotFoundError()
    return Recipe.from_db_recipe(recipe)
