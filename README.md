## Daily Equity Analyser
BSE publishes a "Bhavcopy" (Equity) ZIP every day  [here](https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx)

This web application downloads the equity bhavcopy zip every day at 18:00 IST for the current date and does the following:  
* Extracts and parses the CSV file in it.  
* Writes the records into Redis (Fields: Code, Name, Open, High, Low, Close) with key as name.  The fields have following description:
	* Code:  Unique code assigned to a scrip of a company by BSE.
	* Name: Name of the company.
	* Open: The price at which the security first trades on a given trading day.
	* High: The highest intra-day price of a stock.
	* Low: The lowest intra-day price of a stock.
	* Close: The final price at which a security is traded on a given trading day.
* Renders a simple VueJS frontend with a search box that allows the stored entries to be searched by name and renders a table of results.  
* The search is performed in backend using Redis.

## Setup Instructions
1. Open the terminal and install Redis.
     ```bash
     $ wget http://download.redis.io/redis-stable.tar.gz
     $ tar xvzf redis-stable.tar.gz
     $ cd redis-stable
     $ make
     ```
2. Start the Redis server.
     ```bash
	$ redis-server
	```
3. Make sure you have installed Python 3.6, [pip3](https://pip.pypa.io/en/latest/) and [virtualenv](http://www.virtualenv.org/en/latest/).
4. Keeping the Redis server terminal open, open another new terminal and run the following command
     ```bash
	$ mkdir <project name>
	$ cd <project name>
	$ sudo apt install python3-venv
	$ python3 -m venv <project venv>
	$ source <project venv>/bin/activate
	$ git clone https://github.com/rajats/Levitt-Measure-Prediction-Dashboard.git
	$ cd Daily-Equity-Analyser
	$ pip3 install wheel
	$ pip install -r requirements.txt
     ```
 5. Create .env file by running the following command in the same terminal.
 ```bash
	 $ touch .env
   ```
 6. Open the .env file and write the following environment variables. 
SECRET_KEY, DEBUG, CACHE_BACKEND , CACHE_LOCATION, CACHE_CLIENT_CLASS, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CELERY_TIMEZONE   
An example .env file looks like:
 ```bash
	 SECRET_KEY = '6myxsg0(-u@9^fu)(#-e1l9)axxt^3s@b3p7=$-qw(@$36@lpi'
	 DEBUG = True
	 CACHE_BACKEND = 'django_redis.cache.RedisCache'
	 CACHE_LOCATION = 'redis://127.0.0.1:6379/1'
	 CACHE_CLIENT_CLASS = 'django_redis.client.DefaultClient'
	 CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
	 CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
	 CELERY_TIMEZONE = 'Asia/Kolkata'
   ``` 
 7. To run the periodic task (download everyday at 18:00 IST), we need to start the celery worker and celery beat scheduler. Open a new terminal cd to the project root, activate the **virtual environment** and run the following command to start the celery worker.
 ```bash
	 $ celery -A equity worker -l info
   ```
8. Again open a new terminal cd to the project root, activate the **virtual environment** and run the following command to start the celery beat scheduler.
 ```bash
	 $ celery -A equity beat -l info
   ```
9. Now everything is ready, go back to terminal  where you did ```$ pip install -r requirements.txt``` and run the following command to start the web server.
 ```bash
	 $ python manage.py runserver
   ```

## Deployment Instructions for Heroku
1. Open a new terminal cd to the project root, activate the **virtual environment** and install the Heroku CLI.
 ```bash
	 $ sudo snap install --classic heroku
```
2. Next, run the following commands.
 ```bash
	 $ pip install gunicorn
	 $ pip install whitenoise
	 $ pip freeze > requirements.txt
   ```
 3. Create a Heroku app with Redis addon.
 ```bash
	 $ heroku addons:create heroku-redis:hobby-dev -a <heroku-app-name>
   ```
 4. It's important to change the timezone of Heroku app.
 ```bash
	 $ heroku config:add TZ="Asia/Kolkata"
```
 5. Change the credentials of Redis and Celery Broker with Heroku Redis credential.  To get the Heroku Redis credential type:
 ```bash
	 $ heroku config
```
6. Copy the Heroku Redis URL, open the .env file and replace CACHE_LOCATION, CELERY_BROKER_URL and CELERY_RESULT_BACKEND with the copied Heroku Redis URL. Change DEBUG to False.
7. With free and hobby dyno, you cannot scale to more than 1 dynos per process type. So, use Honcho, install Honcho. 
 ```bash
	 $ pip install honcho
	 $ pip freeze > requirements.txt
```
8. Create a file ProcfileHoncho and add the following.
 ```bash
	 $ web: gunicorn equity.wsgi --log-file -
	 $ worker1: celery -A equity beat -l info
	 $ worker2: celery -A equity worker -l info
```
9. Create a Procfile and add the following.
  ```bash
	 $ web: honcho start -f ProcfileHoncho
   ```
10. Go to  settings<span>.</span>py file add 'whitenoise.middleware.WhiteNoiseMiddleware', in middleware, add 'heroku-app-name<span>.</span>herokuapp<span>.</span>com' in allowed hosts.
11.  Go back to the terminal and run the following commands.
  ```bash
	 $ git add .
	 $ git commit -m "some message" 
	 $ git push heroku master 
   ```
12. Your web application will be live at https<span>://</span>heroku-app-name<span>.</span>herokuapp<span>.</span>com
