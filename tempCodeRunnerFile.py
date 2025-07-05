s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='', region_name='eu-north-1' )

# Connecting to MongoDB
client = MongoClient("")
db = client["LearnArc-StorageMongoDB"]
collection = db["Profiles"]
users_col = db["Profiles"]     # Reference to users collection
chats_col = db["Chats"]        # You should create this collection in MongoDB

# Initializations
app = Flask(__name__)
app.secret_key= ''
socketio = SocketIO(app)