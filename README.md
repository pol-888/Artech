ARTECH

Group Members:
              Aureo, Krystel Mae B.
              Lorica, Khen Mariel M.
              Lacandazo, Danvie
              Cuaycong, Paul Josh A.

How to run the project locally:
1.Clone the repo:
            git clone https://github.com/pol-888/Artech.git
            cd artechweb
2. Create and activate a virtual environment:
      Windows:
            python -m venv venv
            venv\Scripts\activate
      macOS/Linux:
            python3 -m venv venv
            source venv/bin/activate
3. Install dependencies:
          pip install -r requirements.txt
4. Run migrations:
          python manage.py migrate
5. Run the development server:
          python manage.py runserver
6. Open in browser:
          http://127.0.0.1:8000/
7. (Optional) Superuser login:
