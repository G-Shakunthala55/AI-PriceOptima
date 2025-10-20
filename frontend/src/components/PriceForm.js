import React, { useState, useEffect } from 'react';
import axiosClient from '../api/axiosClient';

function PriceForm() {
  // State to store form inputs
  const [formData, setFormData] = useState({
    Time_of_Booking: '',
    Customer_Loyalty_Status: '',
    Vehicle_Type: '',
    Distance_km: '',
    Traffic_Level: '',
    Number_of_Riders: '',
    Number_of_Drivers: '',
    Location_Category: '',
    Number_of_Past_Rides: '',
    Average_Rating: '',
    Expected_Ride_Duration: '',
    Historical_Cost_of_Ride: '',
    competitor_price: ''
  });

  // State to store categories from backend
  const [categories, setCategories] = useState({});

  // State to store recommended price
  const [result, setResult] = useState(null);

  // Fetch categories on mount
  useEffect(() => {
    axiosClient.get('/categories')
      .then(res => setCategories(res.data))
      .catch(err => console.error('Failed to fetch categories:', err));
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Map frontend field names to backend expected names
    const payload = {
      Number_of_Riders: parseFloat(formData.Number_of_Riders),
      Number_of_Drivers: parseFloat(formData.Number_of_Drivers),
      Location_Category: formData.Location_Category,
      Customer_Loyalty_Status: formData.Customer_Loyalty_Status,
      Number_of_Past_Rides: parseFloat(formData.Number_of_Past_Rides),
      Average_Ratings: parseFloat(formData.Average_Rating),
      Time_of_Booking: formData.Time_of_Booking,
      Vehicle_Type: formData.Vehicle_Type,
      Expected_Ride_Duration: parseFloat(formData.Expected_Ride_Duration),
      competitor_price: parseFloat(formData.competitor_price)
    };

    try {
      const response = await axiosClient.post('/recommend', payload);
      setResult(response.data.price_recommended);
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      alert('Something went wrong. Check console for details.');
    }
  };

  return (
    <div style={{ maxWidth: '500px', margin: 'auto', padding: '20px' }}>
      <h2>Dynamic Pricing Form</h2>
      <form onSubmit={handleSubmit}>

        {/* Categorical dropdowns */}
        <select name="Time_of_Booking" value={formData.Time_of_Booking} onChange={handleChange}>
          <option value="">Select Time of Booking</option>
          {categories.Time_of_Booking?.map((t, i) => <option key={i} value={t}>{t}</option>)}
        </select>

        <select name="Customer_Loyalty_Status" value={formData.Customer_Loyalty_Status} onChange={handleChange}>
          <option value="">Select Customer Loyalty Status</option>
          {categories.Customer_Loyalty_Status?.map((t, i) => <option key={i} value={t}>{t}</option>)}
        </select>

        <select name="Vehicle_Type" value={formData.Vehicle_Type} onChange={handleChange}>
          <option value="">Select Vehicle Type</option>
          {categories.Vehicle_Type?.map((t, i) => <option key={i} value={t}>{t}</option>)}
        </select>

        <select name="Location_Category" value={formData.Location_Category} onChange={handleChange}>
          <option value="">Select Location Category</option>
          {categories.Location_Category?.map((t, i) => <option key={i} value={t}>{t}</option>)}
        </select>

        {/* Numeric inputs */}
        <input name="Number_of_Riders" type="number" placeholder="Number of Riders" value={formData.Number_of_Riders} onChange={handleChange} />
        <input name="Number_of_Drivers" type="number" placeholder="Number of Drivers" value={formData.Number_of_Drivers} onChange={handleChange} />
        <input name="Number_of_Past_Rides" type="number" placeholder="Number of Past Rides" value={formData.Number_of_Past_Rides} onChange={handleChange} />
        <input name="Average_Rating" type="number" placeholder="Average Rating" value={formData.Average_Rating} onChange={handleChange} />
        <input name="Expected_Ride_Duration" type="number" placeholder="Expected Ride Duration" value={formData.Expected_Ride_Duration} onChange={handleChange} />
        <input name="competitor_price" type="number" placeholder="Competitor Price" value={formData.competitor_price} onChange={handleChange} />

        <button type="submit" style={{ marginTop: '10px', padding: '10px', backgroundColor: '#4CAF50', color: 'white' }}>Get Price</button>
      </form>

      {result !== null && (
        <p style={{ marginTop: '20px', fontWeight: 'bold' }}>Recommended Price: {result}</p>
      )}
    </div>
  );
}

export default PriceForm;
