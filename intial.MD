I want to build an email reply agent for gamil.
use gmail api to feath everything from the primary inbox.
craft the email response using gemini api key.

There should be a supabase database where the knowelage is stored.
there are courses we support and launch which is where we get mostly an email request regarding that is what the ai agent mostly replied.(As most of the pooples ask about that)
when the reply is crafted it should refer to the document mentioned in the program info..
i need the ability to modify the response crafted by ai before i send it.(as may the user may want to change some thing.)
in the supabase the original response drafted by ai and the one that i send should be stored(it will help the ai agent later to know the person preference well.)
the frontend functionality should have to be deployed in a vercel and the backend functionality have to be deployed in railyway.
you should not automatically send an email with out the user approval with one click.
implement an autentication system so only the gmail owner can use it .
use google login for that .
for every email replying there should be a star rating from 1 t0 5 and a texual feedback system that is stored in a supabase database.

the existing knowelage base in the working directory should be converted in a vector database and stored in a supabase . you should perform rag to feath a relavant info from the vecot database.
The implementations should have to happen in phase first you should have to plan first , asks my preference and then excute in phases.
