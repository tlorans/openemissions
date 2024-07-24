# app/graphql/types.py
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models.carbon_emissions import CarbonEmissionsModel
import re 

class CarbonEmissionsType(SQLAlchemyObjectType):
    class Meta:
        model = CarbonEmissionsModel
        interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    all_emissions = graphene.List(CarbonEmissionsType, skip=graphene.Int(), limit=graphene.Int())
    emissions_by_company = graphene.List(CarbonEmissionsType, company_name=graphene.String(required=True))

    def resolve_all_emissions(self, info, skip=0, limit=10):
        query = CarbonEmissionsType.get_query(info)
        return query.offset(skip).limit(limit).all()

    def resolve_emissions_by_company(self, info, company_name):
        query = CarbonEmissionsType.get_query(info)
        pattern = re.compile(company_name, re.IGNORECASE)
        emissions = query.all()
        return [emission for emission in emissions if pattern.search(emission.name)]

schema = graphene.Schema(query=Query)
