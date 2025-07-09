from mangum import Mangum
from app import app

# Configure Mangum for Lambda
handler = Mangum(app, lifespan="off")
