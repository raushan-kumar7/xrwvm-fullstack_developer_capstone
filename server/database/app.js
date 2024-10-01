const express = require("express");
const mongoose = require("mongoose");
const fs = require("fs");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
const port = 3030;

app.use(cors());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json()); // Added this for handling JSON requests

const reviews_data = JSON.parse(fs.readFileSync("reviews.json", 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync("dealerships.json", 'utf8'));

// Mongoose connection
mongoose.connect("mongodb://mongo_db:27017/", { dbName: "dealershipsDB" })
  .then(() => console.log("Connected to MongoDB"))
  .catch((err) => console.error("Error connecting to MongoDB:", err));

const Reviews = require("./review");
const Dealerships = require("./dealership");

// Database initialization
const initializeDatabase = async () => {
  try {
    await Reviews.deleteMany({});
    await Reviews.insertMany(reviews_data["reviews"]);

    await Dealerships.deleteMany({});
    await Dealerships.insertMany(dealerships_data["dealerships"]);

    console.log("Database initialized successfully.");
  } catch (error) {
    console.error("Error initializing database:", error);
  }
};

// Initialize the database once the server starts
initializeDatabase();

// Express route to home
app.get("/", (req, res) => {
  res.send("Welcome to the Mongoose API");
});

// Fetch all reviews
app.get("/fetchReviews", async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching reviews" });
  }
});

// Fetch reviews by dealership ID
app.get("/fetchReviews/dealer/:id", async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: "Error fetching reviews for dealership" });
  }
});

// Fetch all dealerships
app.get("/fetchDealers", async (req, res) => {
  try {
    const dealerships = await Dealerships.find();
    res.status(200).json(dealerships);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch dealerships" });
  }
});

// Fetch dealers by state
app.get("/fetchDealers/:state", async (req, res) => {
  const { state } = req.params;
  try {
    const stateDealers = await Dealerships.find({ state });
    if (stateDealers.length === 0) {
      return res.status(404).json({ message: `No dealers found in ${state}` });
    }
    res.status(200).json(stateDealers);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch dealerships by state" });
  }
});

// Fetch dealer by ID
app.get("/fetchDealer/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const dealer = await Dealerships.findOne({ id: parseInt(id) });
    if (!dealer) {
      return res.status(404).json({ message: `Dealer with ID ${id} not found` });
    }
    res.status(200).json(dealer);
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch dealer by ID" });
  }
});

// Insert a new review
app.post("/insert_review", async (req, res) => {
  const data = req.body;

  try {
    const lastReview = await Reviews.findOne().sort({ id: -1 });
    const new_id = lastReview ? lastReview.id + 1 : 1;

    const review = new Reviews({
      id: new_id,
      name: data.name,
      dealership: data.dealership,
      review: data.review,
      purchase: data.purchase,
      purchase_date: data.purchase_date,
      car_make: data.car_make,
      car_model: data.car_model,
      car_year: data.car_year,
    });

    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error inserting review" });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
