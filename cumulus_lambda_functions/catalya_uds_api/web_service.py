from cumulus_lambda_functions.catalya_uds_api import auth_admin_api, daac_archive_config_api
from cumulus_lambda_functions.catalya_uds_api import granules_archive_api
from cumulus_lambda_functions.lib.uds_fast_api.fast_api_utils import FastApiUtils
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from mangum import Mangum
from starlette.requests import Request

LOGGER = LambdaLoggerGenerator.get_logger(__name__, LambdaLoggerGenerator.get_level_from_env())

api_base_prefix = FastApiUtils.get_api_base_prefix()
app = FastAPI(title='Unity UDS API',
              description='API to interact with UDS services',
              docs_url=f'/{api_base_prefix}/docs',
              redoc_url=f'/{api_base_prefix}/redoc',
              openapi_url=f'/{api_base_prefix}/openapi',
              )
app.add_middleware(
    CORSMiddleware,
    allow_origins=FastApiUtils.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    LOGGER.error(f"Validation error for {request.url}: {exc.errors()}")
    LOGGER.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

main_router = APIRouter(redirect_slashes=False)
main_router.include_router(auth_admin_api.router)
main_router.include_router(granules_archive_api.router)
main_router.include_router(daac_archive_config_api.router)
app.include_router(main_router, prefix=f'/{api_base_prefix}')


"""
Accept-Ranges:
bytes
Access-Control-Allow-Methods:
HEAD, GET
Access-Control-Allow-Origin:
*
Access-Control-Expose-Headers:
ETag, x-amz-meta-custom-header
Access-Control-Max-Age:
3000
"""

# https://fastapi.tiangolo.com/tutorial/cors/

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

@app.get(f'/{api_base_prefix}/openapi')
@app.get(f'/{api_base_prefix}/openapi/')
async def get_open_api(request: Request):
    default_open_api_doc = app.openapi()
    dropping_keys = [k for k in default_open_api_doc['paths'].keys() if not k.endswith('/')]
    for k in dropping_keys:
        default_open_api_doc['paths'].pop(k)
    return app.openapi()

# to make it work with Amazon Lambda, we create a handler object
handler = Mangum(app=app)

if __name__ == '__main__':
    uvicorn.run("web_service:app", port=8005, log_level="info", reload=True)
    print("running")
