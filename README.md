# Recipe AI App

A comprehensive recipe management application with advanced AI/ML features for recipe analysis, ingredient recognition, nutrition calculation, and meal planning.

## 🏗️ Architecture

The application consists of two main components:

### Frontend (Next.js)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with Radix UI components
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: NextAuth.js
- **File Uploads**: UploadThing

### ML Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Computer Vision**: YOLO v8, CLIP, OpenCV
- **NLP**: spaCy, NLTK, Transformers
- **ML Libraries**: PyTorch, scikit-learn, sentence-transformers
- **Database**: PostgreSQL with SQLAlchemy

## 🚀 Features

### 📸 Food Photo Upload & Analysis
- **Drag & Drop Interface**: Easy image upload with visual feedback
- **Camera Capture**: Direct photo capture on mobile devices
- **Base64 Storage**: Efficient image storage in database
- **Real-time Analysis**: Instant AI-powered food recognition
- **Recipe Generation**: Automatic recipe suggestions based on detected food
- **Nutritional Analysis**: Detailed nutritional information
- **Image History**: Persistent storage of uploaded images and analysis

### Recipe Management
- ✅ Create and upload user-generated recipes
- ✅ Rich image upload with robust photo management
- ✅ Recipe categorization and tagging
- ✅ Search and filter functionality

### AI-Powered Features

#### 🔍 Image to Recipe Analysis
- **Ingredient Recognition**: Advanced computer vision to identify ingredients from food images
- **Recipe Generation**: AI suggests complete recipes based on detected ingredients
- **Confidence Scoring**: Each detected ingredient comes with confidence scores
- **Bounding Box Detection**: Visual localization of ingredients in images

#### 🏷️ AI-Generated Tags
- **Smart Tagging**: Automatically generate relevant tags (vegetarian, gluten-free, quick meal, etc.)
- **Cuisine Detection**: Identify cuisine types from ingredients and cooking methods
- **Dietary Classification**: Automatic detection of dietary restrictions and preferences
- **Cooking Method Analysis**: Tag recipes by cooking techniques (grilled, baked, stir-fry, etc.)

#### 🥗 Nutrition Analysis
- **Comprehensive Calculation**: Detailed nutritional information per serving
- **Ingredient Database**: Extensive nutritional database with unit conversions
- **Portion Estimation**: Smart portion size estimation for better accuracy
- **Dietary Tracking**: Track calories, macros, vitamins, and minerals

#### 🍽️ AI Recipe Recommendations
- **Semantic Search**: Find recipes using natural language queries
- **Dietary Filtering**: Filter by dietary restrictions and preferences
- **Similarity Matching**: Find similar recipes based on ingredients and techniques
- **Personalized Suggestions**: Learn from user preferences and behavior

#### 🍷 Pairing Suggestions
- **Food & Drink Pairings**: AI suggests complementary dishes and beverages
- **Cuisine-Aware**: Culturally appropriate pairing suggestions
- **Seasonal Recommendations**: Suggest pairings based on seasonal ingredients

#### 📅 Meal Planning
- **Personalized Plans**: Generate meal plans based on dietary preferences
- **Balanced Nutrition**: Ensure nutritional balance across meals
- **Shopping Lists**: Automatic generation of ingredient shopping lists
- **Flexible Duration**: Support for 1-14 day meal plans

### Social Features
- ✅ Like/Upvote recipes
- ✅ Save recipes to personal collections
- ✅ "Made" status with user reviews and photos
- ✅ Follow other users and see recipes from your network
- ✅ Recipe reviews and ratings

### Discovery & Trending
- ✅ Trending recipes algorithm
- ✅ Recipe discovery based on user circle
- ✅ Promote featured content creators

### Additional Features
- ✅ Shopping integration potential
- ✅ Chatbot for recipe finding
- ✅ Real-time recipe analysis
- ✅ Multi-language support potential

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ (recommended for ML compatibility)
- PostgreSQL database
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd recipe-ai-app
```

### 2. Setup Frontend (Next.js)

```bash
# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local

# Configure your environment variables:
# - DATABASE_URL: PostgreSQL connection string
# - NEXTAUTH_SECRET: Random secret for NextAuth
# - UPLOADTHING_SECRET: UploadThing API keys
# - ML_BACKEND_URL: ML backend URL (http://localhost:8000)

# Generate Prisma client and run migrations
npx prisma generate
npx prisma db push

# Start the development server
npm run dev
```

### 3. Setup ML Backend (Python)

```bash
# Navigate to ML backend directory
cd ml-backend

# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Configure your environment variables:
# - DATABASE_URL: Same PostgreSQL connection string
# - API_HOST: 0.0.0.0
# - API_PORT: 8000

# Download required models (first run will download automatically)
# - YOLO models (~50MB)
# - Sentence transformers (~100MB)
# - spaCy language models

# Start the ML backend
python run.py
```

### 4. Database Setup

```sql
-- Create PostgreSQL database
CREATE DATABASE recipe_ai_db;

-- The Prisma migrations will handle table creation
```

### 5. Verify Setup

1. **Frontend**: http://localhost:3000
2. **ML Backend**: http://localhost:8000
3. **API Docs**: http://localhost:8000/docs

## 📸 Food Photo Upload Feature

### Usage
1. **Upload Image**: Use the drag & drop area or click "Choose File" to upload a food photo
2. **Analysis**: Click "Analyze" to process the image with AI
3. **View Results**: See detected food, nutritional info, ingredients, and recipe suggestions
4. **History**: All uploaded images are stored and can be viewed in the right panel

### API Endpoints

#### POST /api/recipe-analysis
Upload a food image for analysis.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "filename": "food-photo.jpg"
}
```

**Response:**
```json
{
  "food_name": "Pizza Margherita",
  "confidence": 0.95,
  "calories": 285,
  "cooking_time": 25,
  "ingredients": ["flour", "tomatoes", "mozzarella", "basil"],
  "recipe": "1. Prepare the dough... 2. Add toppings... 3. Bake at 450°F for 20-25 minutes"
}
```

#### GET /api/recipe-analysis
Retrieve all uploaded food images and their analysis.

### Database Schema

#### FoodImage Model
```prisma
model FoodImage {
  id          String   @id @default(cuid())
  filename    String
  base64      String   @db.Text
  uploadedAt  DateTime @default(now())
  analysis    Json?
  userId      String?
  user        User?    @relation(fields: [userId], references: [id], onDelete: Cascade)
  recipeId    String?
  recipe      Recipe?  @relation(fields: [recipeId], references: [id], onDelete: SetNull)
}
```

## 📁 Project Structure

```
recipe-ai-app/
├── src/                          # Next.js frontend
│   ├── app/                      # App router pages
│   │   ├── api/
│   │   │   └── recipe-analysis/  # Food photo analysis API
│   │   ├── components/               # React components
│   │   │   ├── ui/                   # Reusable UI components
│   │   │   ├── ImageUpload.tsx       # Image upload component
│   │   │   └── ImageDisplay.tsx      # Image display component
│   │   ├── lib/                      # Utilities and configurations
│   │   └── styles/                   # CSS and styling
│   ├── ml-backend/                   # Python ML backend
│   │   ├── app/                      # FastAPI application
│   │   │   ├── models/              # ML model implementations
│   │   │   │   ├── food_recognition.py
│   │   │   │   ├── nutrition_analyzer.py
│   │   │   │   ├── recipe_recommender.py
│   │   │   │   └── tag_generator.py
│   │   │   ├── utils/               # Utility functions
│   │   │   ├── schemas.py           # Pydantic models
│   │   │   ├── database.py          # Database configurations
│   │   │   └── main.py              # FastAPI app
│   │   ├── requirements.txt         # Python dependencies
│   │   └── run.py                   # Startup script
│   ├── prisma/                       # Database schema
│   └── public/                       # Static assets
└── README.md                     # This file
```

## 🤖 ML Models & Techniques

### Computer Vision
- **YOLO v8**: Object detection and ingredient localization
- **CLIP**: Semantic understanding of food images
- **ResNet**: Custom food classification

### Natural Language Processing
- **Sentence Transformers**: Recipe similarity and search
- **spaCy**: Named entity recognition and linguistic analysis
- **NLTK**: Text preprocessing and tokenization
- **TF-IDF**: Keyword matching and relevance scoring

### Machine Learning
- **Cosine Similarity**: Recipe recommendation scoring
- **Clustering**: Ingredient categorization
- **Feature Engineering**: Nutritional analysis and portion estimation
- **Rule-based Systems**: Dietary classification and pairing suggestions

## 🔧 API Endpoints

### ML Backend Endpoints

- `POST /analyze-food-image` - Analyze uploaded food images
- `POST /generate-recipe-tags` - Generate AI tags for recipes
- `POST /analyze-nutrition` - Calculate nutritional information
- `POST /generate-pairings` - Generate food/drink pairings
- `POST /recommend-recipes` - Find recipes by criteria
- `POST /generate-meal-plan` - Create personalized meal plans
- `POST /analyze-recipe-complete` - Complete recipe analysis
- `GET /health` - Health check
- `GET /models/status` - ML model status

## 🚀 Deployment

### Frontend Deployment (Vercel)
```bash
# Build and deploy
npm run build
# Deploy to Vercel or your preferred platform
```

### ML Backend Deployment

#### Docker Deployment
```dockerfile
# Dockerfile for ML backend
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

#### Production Considerations
- Use GPU instances for better ML performance
- Implement model caching and optimization
- Setup load balancing for high traffic
- Use Redis for caching ML results
- Monitor model performance and accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🐛 Known Issues & Future Improvements

### Current Limitations
- ML models download on first run (initial startup time)
- Image processing can be memory intensive
- Some nutrition data may be approximate

### Planned Features
- Mobile app support
- Offline recipe access
- Voice recipe instructions
- Integration with smart kitchen appliances
- Advanced meal planning with calendar integration
- Recipe cost estimation
- Allergen detection and warnings

## 📞 Support

For issues and questions:
1. Check the GitHub Issues page
2. Review the API documentation at `/docs`
3. Check model status at `/models/status`

---

Built with ❤️ using Next.js, FastAPI, and cutting-edge ML techniques.
