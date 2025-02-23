# Econome
A FastAPI project that helps users create recipes from their available ingredients, reducing food waste and inspiring creative cooking.

## Overview
Econome solves a problem I often face myself; not knowing what to cook with leftover ingredients. Using Mistral's SDK it generates recipes from both text descriptions and images of ingredients (e.g the inside of a fridge).

## Quick Links
- [API Documentation](http://localhost:8000/docs)
- [ReDoc Interface](http://localhost:8000/redoc)
- [API Endpoints](#api-endpoints)
- [Setup Instructions](#setup)
- [Testing](#testing)

## Features
- Recipe generation from text input
- Recipe generation from images (using Mistral's Vision API)
- Recipe storage and management (CRUD operations)
- Optional recipe illustrations using [FAL.ai](https://fal.ai)

## Implementation Details
- Python 3.13
- FastAPI
- Mistral SDK
- MongoDB (to enable faster prototyping)
- Modern UV package manager
- Extensive logging and exception handling

## Getting Started

### Prerequisites
- Docker
- Mistral API key
- [FAL.ai](https://fal.ai/dashboard/keys) API key (optional, for flux recipe illustrations) 

### Environment Setup
1. Create a `.env` file in the project root:
```env
MISTRAL_KEY=<your-mistral-key>
FAL_KEY=<your-fal-key>  # Optional
```

2. Start the application from the top level:
```bash
> docker compose up
```

The server will be available at `0.0.0.0:8000`

## API Endpoints

### Generate Recipe [POST /api/recipes]
Generates a recipe and optional illustration from a list of ingredients.

#### Request
```json
[
    {
        "name": "sirloin steak",
        "quantity": "500g"
    },
    {
        "name": "bell peppers",
        "quantity": "2"
    },
    {
        "name": "soy sauce",
        "quantity": "500ml"
    },
    {
        "name": "oyster sauce",
        "quantity": "500ml"
    },
    {
        "name": "sesame oil",
        "quantity": "500ml"
    }
]
```

#### Response
```json
{
    "meal": "Soy-Sesame Beef Stir-Fry",
    "steps": [
        {
            "content": "Cut the 500g of sirloin steak into thin strips, ensuring you're cutting against the grain for tenderness."
        },
        {
            "content": "Slice the 2 bell peppers into thin strips as well, then set them aside."
        },
        {
            "content": "In a bowl, mix together 250ml of soy sauce and 250ml of oyster sauce. This will be your sauce base."
        },
        {
            "content": "Heat a large pan or wok over medium-high heat and add 1 tablespoon of the 500ml of sesame oil."
        },
        {
            "content": "Once the oil is hot, add the beef strips and cook until browned and cooked through. Remove the beef from the pan and set it aside."
        },
        {
            "content": "In the same pan, add another tablespoon of sesame oil. Add the sliced bell peppers and cook until they begin to soften."
        },
        {
            "content": "Pour the soy and oyster sauce mixture into the pan with the peppers. Stir well to combine."
        },
        {
            "content": "Return the cooked beef to the pan and stir to coat everything evenly in the sauce."
        },
        {
            "content": "Cook for an additional 2-3 minutes to allow the flavors to meld together."
        },
        {
            "content": "Drizzle a small amount of sesame oil over the top before serving for added flavor."
        },
        {
            "content": "Serve hot with steamed rice or noodles."
        }
    ],
    "image_url": "https://fal.media/files/panda/T4KFDFAcIle1MAcGh6GHY_f5a4d26c3ca44e81b135171a389d48be.jpg"
}
```

### Additional Endpoints

- **Generate Recipe from Image** [POST /api/recipes/vision]  
  Generate a recipe from an image of ingredients

- **Save Recipe** [POST /api/recipes/save]  
  Store a recipe in the database

- **Delete Recipe** [DELETE /api/recipes]  
  Remove a recipe from storage

- **Get Recipe** [GET /api/recipes/{id}]  
  Retrieve a specific recipe by ID

- **List Recipes** [GET /api/recipes/]  
  Retrieve all saved recipes

# Testing
For the best testing experience, you can access the interactive API documentation at:

- [Swagger UI Documentation](http://localhost:8000/docs) - Interactive API testing interface
- [ReDoc Documentation](http://localhost:8000/redoc) - Alternative documentation viewer


To test the API:


1. Start the server using `docker compose up`
2. Navigate to [`http://localhost:8000/docs`](http://localhost:8000/docs)
3. Click on any endpoint to expand it
4. Click "Try it out" and input your test data
5. Execute the request and view the results