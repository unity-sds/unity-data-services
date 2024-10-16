import uvicorn

from cumulus_lambda_functions.uds_api.web_service import app

uvicorn.run(app, port=8005, log_level="info", reload=True)
