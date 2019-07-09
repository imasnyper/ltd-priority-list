import graphene
import graphql_jwt

import list.schema


class AuthenticationMutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(list.schema.Query, graphene.ObjectType):
    pass


class Mutation(AuthenticationMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
