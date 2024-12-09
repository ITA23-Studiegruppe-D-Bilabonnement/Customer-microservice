from flasgger import Swagger

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "specs": [
                {
                    "endpoint": 'login',
                    "route": '/login',
                    "spec": '/swagger/login.yaml'
                },
                {
                    "endpoint": 'register',
                    "route": '/register',
                    "spec": '/swagger/register.yaml'
                },
                {
                    "endpoint": 'delete',
                    "route": '/delete/<int:id>',
                    "spec": '/swagger/delete.yaml'
                },
                {
                    "endpoint": 'user',
                    "route": '/user',
                    "spec": '/swagger/user_information.yaml'
                }

            ],
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

template = {
    "info": {
        "title": "Customer microservice",
        "description": "Customer microservice that handles users",
        "version": "1.0.0",
        "contact": {
            "name": "KEA",
            "url": "https://kea.dk"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        }
    }
}

def init_swagger(app):
    """Initialize Swagger with the given Flask app"""
    return Swagger(app, config=swagger_config, template=template)