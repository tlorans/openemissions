# app/api/v1/endpoints/graphql.py
from fastapi import APIRouter
from starlette.graphql import GraphQLApp
from app.graphql.types import schema

router = APIRouter()
router.add_route("/", GraphQLApp(schema=schema))
