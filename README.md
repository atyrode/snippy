# vite!

✂️ Sharpen your links with **vite!** API.

# How?

To get started and self host your **vite!** API, follow these steps:

1. First, git clone the project somewhere then `cd` into it.
```shell
git clone git@github.com:atyrode/vite.git
cd vite
```

2. Create a .env file containing the keys VITE_PROTOCOL & VITE_HOST
 with your prefered values (e.g. below) or set them as environment variables:
```
VITE_PROTOCOL=https
VITE_HOST=localhost:8080
```

3. Using Python 3.9 or up, run:
```shell
pip install -r requirements.txt
python3 start.py
```

4. Voilà! As a French person, would say: "c'est allé [vite, lol](http://vite.lol/)"

# Then what?

**vite!** is a [FastAPI](https://fastapi.tiangolo.com/) based API that serves 4 different endpoints to get shortened links on URL or text value:

### - /encode
Takes in a `value` argument (as `/encode?value=`) that can be an URL or text and returns a JSON response containing an `url` key of the format: `https://localhost:8080/` followed by a unique ID.

> **Note**: The results of the encoding are predictable and not obfuscated.
> This lets **vite!** benefits from very shorts URL for a good amount of encoding ⚡


### - /decode
Takes in an `url` argument (as `/decode?url=`) that can be of the following three formats:

- `https://localhost:8080/aB5f`
- `localhost:8080/aB5f`
- `aB5f`

And returns a JSON response containing a `value` (the original encoded URL or text) as well as a `clicks` key. `clicks` represent the amount of time your link was used by `/redirect` (refer below)


### - /determine
Takes in a `query` argument (as `/determine?query=`) and will attempt to redirect your query on the `/encode` or `/decode` endpoint and will return their respective result JSON.


### - /redirect/
Redirection is an endpoint that can explicitly be called with `/redirect/` or implicitly on `/` that can be followed by the three following format:

- `https://localhost:8080/aB5f`
- `localhost:8080/aB5f`
- `aB5f`

If the shortened link points on text, it will return a JSON response containing a `text` key.
If the shortened link points to an URL, it will redirect you there.

# And now?

You're set. `start.py` will run **vite!** using `uvicorn`, which will let you make requests on `localhost:8080` at the endpoints mentioned above.

As a bonus, and if you want to use it like a regular URL shortener, you can access its front page on `localhost:8080/` in your browser of choice.

Finally, you can access `localhost:8080/docs/` (<- don't forget the trailing `/`) to get the documentation (**Swagger**) of the **vite!** API!

And of course, if you host this somewhere (at your `VITE_HOST` domain), then replace localhost by your `VITE_HOST` in these examples.

# Good bye!

This project is open to contributions, it was made in the scope of technical assessment with limited time, I have covered as much as I could of the basic implementation and there should be a test suite for each component of **vite!**.

I will most likely come back to it in my free time to polish the web client, optimize the back end, and switch to a more scalable database system.
