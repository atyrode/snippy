# Snippy

✂️ Sharpen your links with **snippy** API.

# What?

**snippy** is a [FastAPI](https://fastapi.tiangolo.com/) based API that serves 4 different endpoints:

- `/encode?url=`
- `/decode?url=` 

Both of these takes an URL as argument and respectively `encode` or `decode` it. It is not meant to be private or obfuscated, it `decode` into its database row unique id count and `encode` on a base 62.

- `/determine?url=`

`determine` will attempt at 'guessing' whether the request is trying to ``encode`` or ``decode`` an URL and redirect accordingly.

Finally, through multiple endpoints formats:

- `/redirect/`

As `/redirect/` then a shortened URL, it's unique ID, or simply by appending the unique ID to the root `/` endpoint will redirect you to where an `encoded` links point to.

# How?

To get started and self host your **snippy** API, follow these steps:

1. First, git clone the project somewhere then `cd` into it.
```shell
git clone git@github.com:atyrode/snippy.git
cd snippy
```

2. Using Python 3.9 or up, run:
```shell
pip install -r requirements.txt
python3 start.py
```

3. Voilà! As a French person, would say: "c'est allé [vite, lol](http://vite.lol/)"

# And now?

You're set. `start.py` will run **snippy** using `uvicorn`, which will let you make requests on `localhost:8080` at the endpoints mentioned above.

As a bonus, and if you want to use it like a regular URL shortener, you can access its front page on `localhost:8080/` in your browser of choice.


# Good bye!

This project is open to contributions, it was made in the scope of technical assessment with limited time, I have covered as much as I could of the basic implementation and there should be a test suite for each component of **snippy**.

I will most likely come back to it in my free time to polish the web client, optimize the back end, and switch to a more scalable database system.
