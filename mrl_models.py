import requests
import json
from pydantic import BaseModel, Field, Extra
from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ✅ Define a Peer Model
class Peer(BaseModel):
    name: str
    type: str
    autoStart: bool
    class_: str = Field(alias="class")  # Fix for reserved keyword

# ✅ Define Service Dependency Model
class ServiceDependency(BaseModel):
    groupId: str
    artifactId: str
    version: Optional[str]
    ext: str
    installed: bool
    includeInOneJar: bool
    skipped: bool
    excludes: List[str]
    artifacts: List[str]
    class_: str = Field(alias="class")  # Fix for reserved keyword

# ✅ Define ServiceType Model
class ServiceType(BaseModel):
    available: bool
    installed: bool
    dependencies: List[ServiceDependency]
    description: str
    includeServiceInOneJar: bool
    isCloudService: bool
    type: str
    requiresKeys: bool
    simpleName: str
    class_: str = Field(alias="class")  # Fix for reserved keyword

# ✅ Define InMoov2Config Model (Now includes gestures!)
class InMoov2Config(BaseModel):
    type: str
    peers: Dict[str, Peer]
    gestures: List[str] = []  # ✅ Added support for gestures
    class_: str = Field(alias="class")  # Fix for reserved keyword

# ✅ Define InMoov2 Model
class InMoov2(BaseModel):
    serviceType: ServiceType
    config: InMoov2Config
    name: str
    id: str
    simpleName: str
    typeKey: str
    isRunning: bool
    #gestures: List[str] = []  # ✅ Adding gestures at the top-level for easy access
    class_: str = Field(alias="class")  # Fix for reserved keyword

    gestures: List[str] = Field(default_factory=list)

    def get_gestures(self) -> List[str]:
        """Returns the list of available gestures."""
        return self.gestures

    @classmethod
    def from_json(cls, json_data: dict):
        """Creates an instance of InMoov2 from JSON data."""
        gestures = json_data.get("gestures", [])  # Extract gestures list
        return cls(gestures=gestures)


# ✅ Function to fetch JSON and convert to InMoov2 object
def get_inmoov2_instance():
    url = "http://localhost:8888/api/service/i01"

    try:
        response = requests.get(url)
        response.raise_for_status()  # ✅ Raise error if request fails

        json_data = response.json()  # ✅ Convert to Python dictionary
        inmoov_instance = InMoov2(**json_data)  # ✅ Map JSON to Pydantic Model

        return inmoov_instance  # ✅ Return mapped object

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except Exception as e:
        print(f"Error processing JSON response: {e}")
        return None

# # ✅ Example Usage:
# inmoov = get_inmoov2_instance()
# if inmoov:
#     print(f"InMoov2 Service Name: {inmoov.name}")
#     print(f"Running Status: {inmoov.isRunning}")
#     print(f"Number of Peers: {len(inmoov.config.peers)}")