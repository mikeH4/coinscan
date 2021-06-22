import settings
from fastapi import APIRouter,HTTPException,Header
from core.misc.ViewableListings import ViewableListings

from typing import List,Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/private"
)

def check_api_key(auth):
    if settings.sandbox == True:
        return True
    if auth != "j23j90rhn)#@p23j09h)*IH#@)(H#@IRJT)I@#HT(FH@#N)TJ_(@IHNof j4900tjf0t34":
        raise HTTPException(status_code=404, detail="Not Found")

class Listing(BaseModel):
    platform: str
    name: str

@router.post("/from-listings")
async def new_tokens(
    listings:List[Listing],
    auth: Optional[str] = Header("")
):
    check_api_key(auth)
    if len(listings) < 1:
        return []
    listifyed = [[item.platform,item.name] for item in listings]
    return ViewableListings.from_slug(listifyed)