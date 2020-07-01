# **Le vélo rouge** blog
**REQUIRES**: Python >= 3.6.6, Django >= 3.0.7 and other packages specified in 'reqs.txt'


## How to use it:

  1) Clone or download the source code. Create a virtual enviroment (venv) with `python -m venv mynewvirtualenv`. 
      A folder called 'mynewvirtualenv' will be created
    
  2) Go inside the 'mynewvirtualenv' folder, then go inside 'Scripts' folder and activate the 
     virtual enviroment with `. activate`, then go back to the root of the proyect

  3) Install pip, update it if necessary; do it with `python -m pip install --upgrade pip`. Then install the 
  required packages with the command `pip install -r reqs.txt`
     
  4) Run migrations with `python manage.py migrate`
  
  5) Create a superuser with `python manage.py createsuperuser` and fill the required info

  **IMPORTANT**: After step 5 a blog_author object must be created, this object will have a One To One relation 
  with the superuser due the models are configured that way to create also an author when a user is created. 
  In production, the blog_author object for the superuser isn't actually required (that's why neither the slug, email 
  or bio are needed) but it is required at the set-up moment in order not to produce an error that says that 
  the blog_author instance is missing. Now we'll see how to avoid this and create the object from the python shell

    * Open the interactive shell: `python manage.py shell`, then import the model with `from MyApp.models import blog_author` 
    * Import the superuser: `from django.contrib.auth.models import User`, you can verify if the superuser has been created with 
    `User.objects.all()` - You'll see the user you've created in step 5.
    * Create the supusr object with `supusr = User.objects.get(username='Username')`, Username is the same you wrote in step 5
    * Then create the blog_author object with `blog_author.objects.create(name=supusr)` and that's it
    
  6) Go to the root project folder and run the server with `python manage.py runserver`
  
For further information read the *DjangoTutorial.txt* file

**NOTE**: Don't forget to install Node dependencies with `npm install`
