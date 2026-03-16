from drf_spectacular.utils import extend_schema,extend_schema_view,OpenApiParameter,OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(
        summary='List all Posts',
        description='This is a descp of extended schema',
        parameters=[
            OpenApiParameter(
                name='published',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by publication status',
            ),
            OpenApiParameter(
                name='author',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by author ID'
            )
        ],
        responses=
    )
)