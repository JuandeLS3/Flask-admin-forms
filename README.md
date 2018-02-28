# Flask admin forms example

This example shows how you can define your own custom forms by using form rendering rules. It also demonstrates general file handling as well as the handling of image files specifically.

## Simple CRUD
This example can perform insert, edit and delete operations.

## To run this example
Clone the repository.

		git clone https://github.com/JuandeLS3/Flask-admin-forms.git
			

Create and activate a virtual environmen

		virtualenv env
		source env/bin/activate

Install requirements.

		pip install -r "requirements.txt"

Run the application

		python app.py

The first time you run this example, **a sample sqlite database gets populated automatically**. To suppress this behaviour, comment the following lines in **/app.py**.

		if not os.path.exists(database_path):
		    build\_sample\_db()

## Authors

**Serge S. Koval** - *Initial work* - [mrjoes](https://github.com/flask-admin/flask-admin/commits?author=mrjoes)

## License

This project is licensed under the Apache 2.0 - see the [LICENSE](https://github.com/JuandeLS3/Flask-admin-forms/blob/master/LICENSE "LICENSE") file for details
