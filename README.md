
# Blog Website Project

This is a blog website built using Flask, SQLAlchemy, and MySQL. The application allows users to register, log in, and create blog posts. Users can also comment on posts, and the website includes pagination to navigate through posts efficiently. An admin panel is available to manage blog content, and the site has an integrated contact form that sends emails using SMTP.

## Features

- **User Authentication**: Users can sign up, log in, and log out.
- **Blog Posts**: Registered users can create, edit, and delete blog posts.
- **Comments**: Users can comment on blog posts.
- **Admin Panel**: Admins can manage all posts and view a dashboard of the blogs.
- **Rich Text Editing**: CKEditor integration for editing blog posts with rich text.
- **Pagination**: Blogs are displayed with pagination, showing 4 posts per page.
- **Contact Form**: Users can send messages via a contact form, which sends an email to the admin.
- **Responsive Design**: Frontend is responsive and user-friendly across devices.

## Technologies Used

- **Flask**: A lightweight web framework for Python.
- **SQLAlchemy**: ORM for interacting with the MySQL database.
- **MySQL**: Database to store user, blog post, and comment data.
- **Flask-Login**: For user session management and authentication.
- **Flask-CKEditor**: Rich text editor integration for blog content.
- **Werkzeug**: For hashing passwords and securing user data.
- **Bootstrap**: Used for styling and responsive design.
- **SMTP**: For sending emails via the contact form.

## Setup and Installation

### Prerequisites

- Python 3.x
- MySQL
- Flask and required Python packages (see `requirements.txt`)

### Steps to Install

1. Clone this repository:
   ```bash
   git clone https://github.com/Maroa2002/Webstack---Portfolio-Project.git
   cd your-repo
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - `DB_PWD`: MySQL password for the `root` user.
   - `SECRET_KEY`: Flask secret key.
   - `GMAIL_PASSWORD`: Password for the Gmail account to use for sending contact emails.

5. Set up your MySQL database:
   ```sql
   CREATE DATABASE blog_db;
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Open your browser and navigate to `http://127.0.0.1:5000/`.

## Database Models

- **User**: Represents users with `id`, `name`, `email`, and `password`.
- **Post**: Represents blog posts with `id`, `title`, `subtitle`, `date`, `body`, and `img_url`. Linked to the `User` model via `author_id`.
- **Comment**: Represents comments on posts with `id`, `body`, `date_posted`, `author_id`, and `post_id`.

## Routes

- `/` - Home page displaying paginated blog posts.
- `/login` - Login page for users.
- `/signup` - Signup page for new users.
- `/post/<int:post_id>` - View an individual post and its comments.
- `/dashboard` - Admin dashboard for viewing and managing posts.
- `/new-post` - Create a new blog post (requires login).
- `/edit-post/<int:post_id>` - Edit an existing blog post (requires login).
- `/delete-post/<int:post_id>` - Delete a blog post (admin only).
- `/about` - About page.
- `/contact` - Contact form for sending emails to the admin.

## Admin Functionality

Only users with `id = 1` (admin) have access to the admin dashboard and can delete posts. You can customize this functionality based on your needs by modifying the `admin_only` decorator.

## Future Improvements

- **File Uploads**: Allow users to upload images for their blog posts.
- **User Profiles**: Create user profiles to show individual user activity (posts, comments).
- **Email Confirmation**: Add email confirmation during signup for added security.
- **Full-text Search**: Implement a search feature to allow users to search for blog posts.

