# Demo Script (2-3 minutes)

1. **Introduction (Home Page)**
   - Open the app at `http://localhost:5173`.
   - Show the map centered on the default location.
   - Explain the purpose: "Crowdsourcing neighborhood issues to find hotspots."

2. **Submit a Report**
   - Click "New Report".
   - Fill in:
     - Title: "Pothole on Main St"
     - Category: "Infrastructure"
     - Description: "Deep pothole causing traffic."
     - Click "Get Current Location" (or enter lat/lon).
     - Upload an image (optional).
   - Click "Submit".
   - Show the success alert and redirection to the map.
   - Verify the new marker appears on the map.

3. **Duplicate Detection**
   - Click "New Report" again.
   - Enter a location very close to the previous one.
   - Show the "Similar Reports Nearby" warning appearing.
   - Explain: "This prevents duplicate data and encourages upvoting."

4. **Upvote**
   - Click on the marker of the report just created.
   - Click the "Upvote" button (if visible in popup, or mention the API capability).
   - *Note: UI for upvote button in popup might need to be verified.*

5. **Hotspots & Analysis**
   - Navigate to "Hotspots" page.
   - Show the list of top hotspots.
   - Explain: "These are clusters of reports computed server-side using K-Means."
   - Click "Export CSV" to download the data.

6. **Backend API**
   - Briefly show `http://localhost:8000/docs`.
   - Highlight the `GET /hotspots` endpoint options (grid vs kmeans).
