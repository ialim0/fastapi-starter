# FastAPI Auth Starter

This is a FastAPI starter code for setting up authentication quickly and efficiently. It provides a flexible solution that can be adapted to various types of applications, from small projects to complex SaaS products.

## Features

- Quick setup for user authentication
- Flexible enough to work with different kinds of apps
- Supports multiple authentication providers (Google, GitHub, LinkedIn)
- Customizable to fit your specific needs
- Includes `pytest` for authentication testing

## Getting Started

### Prerequisites

- Python 3.7+
- FastAPI
- SQLite (or any other database supported by SQLAlchemy)
- pytest (for running tests)

### Installation

Clone the repository:

```bash
git clone https://github.com/ialim0/fastapi-starter
cd fastapi-auth-starter
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory of the project and add the following environment variables:

```bash
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./test.db

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI="http://127.0.0.1:8000/auth/google/callback"

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI="http://127.0.0.1:8000/auth/github/callback"

LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI="http://127.0.0.1:8000/auth/linkedin/callback"
```

### Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Open your browser and navigate to `http://127.0.0.1:8000` to see the application in action.

## Usage

### Authentication Providers

This starter code supports multiple authentication providers:

- **Google**: Use the `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` environment variables to configure Google authentication.
- **GitHub**: Use the `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `GITHUB_REDIRECT_URI` environment variables to configure GitHub authentication.
- **LinkedIn**: Use the `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, and `LINKEDIN_REDIRECT_URI` environment variables to configure LinkedIn authentication.

### Customization

The starter code is designed to be flexible and customizable. You can easily adapt it to fit the specific needs of your application. Whether you're handling standard login/password systems or more complex roles and permissions, this starter code can give you a jump start.

## Running Tests

This project includes `pytest` for testing the authentication functionality. To run the tests, follow these steps:

Ensure you have pytest installed:

```bash
pip install pytest
```

Run the tests:

```bash
pytest
```

The tests are located in the `tests` directory. You can add more tests as needed to ensure the robustness of your authentication system.

## Contributing

We welcome contributions to this project! If you have suggestions, improvements, or bug fixes, please feel free to open an issue or submit a pull request. Your contributions help make this project better for everyone.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

Thanks to the FastAPI community for their excellent documentation and support.  
Special thanks to the maintainers of the libraries used in this project.