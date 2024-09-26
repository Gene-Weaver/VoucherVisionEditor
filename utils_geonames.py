import geocoder

def search_location(query, GEONAMES_USERNAME):
    """Search for the location using geocoder and GeoNames, excluding feature class 'S'."""
    # Exclude feature class 'S' (Spot, Building, Farm, etc.)
    g = geocoder.geonames(query, key=GEONAMES_USERNAME, maxRows=10, featureClass=['A', 'P', 'T', 'H', 'L', 'R', 'V', 'U'])
    
    if g:
        if len(g) == 1:  # If there's exactly one result
            print(f"Single result found: {g[0].address} (GeoNames ID: {g[0].geonames_id})")
            return g[0].geonames_id
        elif len(g) > 1:  # If there are multiple results
            print("Multiple results found. Possible locations:")
            for result in g:
                print(f"- {result.address} (GeoNames ID: {result.geonames_id})")
            return None  # No single result to show the hierarchy for
    else:
        print(f"No results found for: {query}")
        return None

def get_hierarchy(geoname_id, GEONAMES_USERNAME):
    """Fetch the hierarchy for a given GeoNames ID."""
    h = geocoder.geonames(geoname_id, key=GEONAMES_USERNAME, method='hierarchy')
    
    if h:
        print("Location hierarchy:")
        for place in h:
            print(f"{place.address} ({place.description})")
    else:
        print(f"No hierarchy found for GeoNames ID: {geoname_id}")

def get_location_hierarchy(stated_country, stated_stateProvince, stated_county, stated_locality, GEONAMES_USERNAME):
    """
    Get the location hierarchy by progressively reducing the query string if no results are found.
    """
    # Build the full query string, starting with the most detailed (locality, county, stateProvince, country)
    query_parts = [stated_locality, stated_county, stated_stateProvince, stated_country]
    
    # Keep trying by removing the smallest (left-most) part of the hierarchy until something works
    for i in range(len(query_parts)):
        # Create query by joining non-empty parts
        query = ", ".join([part for part in query_parts[i:] if part])
        
        if query:
            print(f"Searching for location: {query}")
            geoname_id = search_location(query, GEONAMES_USERNAME)
            
            if geoname_id:
                get_hierarchy(geoname_id, GEONAMES_USERNAME)
                return  # Exit after the first successful search and hierarchy fetch
    
    # If no data found at any level, return None
    print("No valid region found for the specified inputs.")

# Example usage
stated_country = "USA"
stated_stateProvince = "Colorado"
# stated_county = "El Paso"
stated_county = ""
# stated_locality = "Garden of the Gods, Colorado Springs"
stated_locality = "Pike National Forest"

get_location_hierarchy(stated_country, stated_stateProvince, stated_county, stated_locality, GEONAMES_USERNAME='vouchervision')
