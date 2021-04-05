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
1. Open terminal and install Redis
     ```bash
     $ wget http://download.redis.io/redis-stable.tar.gz
     $ tar xvzf redis-stable.tar.gz
     $ cd redis-stable
     $ make
     ```
2. Start the Redis server by:
     ```bash
	$ redis-start
	```
3. Make sure you have installed Python 3.6, [pip3](https://pip.pypa.io/en/latest/) and [virtualenv](http://www.virtualenv.org/en/latest/).
4. Keeping the Redis server terminal open, open another new terminal and run the following command
     ```bash
	$ mkdir <project name>
	$ cd <project name>
	$ sudo apt install python3-venv
	$ python3 -m venv <project venv>
	$ source <project venv>/bin/activate
	$ git clone [https://github.com/rajats/Levitt-Measure-Prediction-Dashboard.git](https://github.com/rajats/Levitt-Measure-Prediction-Dashboard.git)
	$ cd Daily-Equity-Analyser
	$ pip3 install wheel
	$ pip install -r requirements.txt
     ```
 5. To run the periodic task (download everyday at 18:00 IST), we need to start the celery worker and celery beat scheduler. Open a new terminal in the **virtual environment** and run the following command to start the celery worker.
 ```bash
	 $ celery -A equity worker -l info
   ```
5. Again open a new terminal in the **virtual environment** and run the following command to start the celery beat scheduler.
 ```bash
	 $ celery celery -A equity beat -l info
   ```
6. Now everything is ready, go back to terminal  where you did ```$ pip install -r requirements.txt``` and run the following command to start the web server.
 ```bash
	 $ python manage.py runserver
   ```

