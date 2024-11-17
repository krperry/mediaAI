import requests  # Import the requests library to make HTTP requests
import xml.etree.ElementTree as ET  # Import the ElementTree library to parse XML

class TuneInAPI:
    """
    A class to interact with the TuneIn API.
    """
    BASE_URL = "http://opml.radiotime.com/"  # Base URL for the TuneIn API
    
    def search_stations(self, query):
        """
        Search for radio stations based on a query.
        
        Args:
            query (str): The search query for stations.
        
        Returns:
            list: A list of dictionaries containing station information.
        """
        try:
            # Make the request to the TuneIn API
            response = requests.get(f"{self.BASE_URL}Search.ashx", params={"query": query})
            # Raise an exception if the request was not successful
            response.raise_for_status()
            print(f"Response content: {response.content}")  # Debug statement
            with open("response_content.xml", "wb") as f:
                f.write(response.content)
            # Parse the response content as XML
            return self.parse_xml(response.content)
        except requests.RequestException as e:
            print(f"Error searching stations: {e}")
            return []
    
    def get_station_stream_url(self, station_id):
        """
        Get the stream URL for a specific station.
        
        Args:
            station_id (str): The ID of the station.
        
        Returns:
            str: The stream URL of the station.
        """
        try:
            # Make the request to the TuneIn API
            response = requests.get(f"{self.BASE_URL}Tune.ashx", params={"id": station_id})
            # Raise an exception if the request was not successful
            response.raise_for_status()
            # Resolve the stream URL from the response content
            return self.resolve_stream_url(response.content)
        except requests.RequestException as e:
            print(f"Error getting station stream URL: {e}")
            return ""
    
    def parse_xml(self, xml_content):
        """
        Parse the XML content to extract station information.
        
        Args:
            xml_content (bytes): The XML content to parse.
        
        Returns:
            list: A list of dictionaries containing station information.
        """
        stations = []
        root = ET.fromstring(xml_content)
        for outline in root.findall(".//outline[@type='audio']"):
            station = {
                "text": outline.get("text"),
                "URL": outline.get("URL"),
                "bitrate": outline.get("bitrate"),
                "reliability": outline.get("reliability"),
                "guide_id": outline.get("guide_id"),
                "subtext": outline.get("subtext"),
                "genre_id": outline.get("genre_id"),
                "formats": outline.get("formats"),
                "item": outline.get("item"),
                "image": outline.get("image"),
                "current_track": outline.get("current_track"),
                "now_playing_id": outline.get("now_playing_id"),
                "preset_id": outline.get("preset_id"),
            }
            stations.append(station)
        return stations
    
    def resolve_stream_url(self, content):
        """
        Resolve the stream URL from the content.
        
        Args:
            content (bytes): The content to resolve the stream URL from.
        
        Returns:
            str: The resolved stream URL.
        """
        # Check if the content is a playlist and extract the actual stream URL
        content_str = content.decode('utf-8')
        if content_str.startswith("#EXTM3U"):
            # M3U playlist
            for line in content_str.splitlines():
                if line and not line.startswith("#"):
                    return line
        elif content_str.startswith("[playlist]"):
            # PLS playlist
            for line in content_str.splitlines():
                if line.startswith("File1="):
                    return line.split("=", 1)[1]
        return content_str
