from fastapi.staticfiles import StaticFiles

from cumulus_lambda_functions.uds_api.fast_api_utils import FastApiUtils
from cumulus_lambda_functions.lib.lambda_logger_generator import LambdaLoggerGenerator
from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mangum import Mangum
from starlette.requests import Request

from cumulus_lambda_functions.uds_api.routes_api import main_router
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
app.include_router(main_router, prefix=f'/{api_base_prefix}')

stac_browser_prefix, temp_static_parent_dir = FastApiUtils.prep_stac_browser()
app.mount(stac_browser_prefix, StaticFiles(directory=temp_static_parent_dir, html=True), name="static")
app.mount(f'/{stac_browser_prefix}/', StaticFiles(directory=temp_static_parent_dir, html=True), name="static")

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
