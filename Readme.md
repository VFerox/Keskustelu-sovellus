# Text&Chat – Muistiinpanosovellus

## Yleiskatsaus
Flask-pohjainen muistiinpano- ja keskustelusovellus  
Käyttäjät voivat luoda tilin, lisätä muistiinpanoja, vastata niihin, tykätä/ei-tykätä ja hakea.

## Asennus
```bash
python -m venv venv
venv\Scripts\activate
pip install Flask Faker 
python load_test.py        
flask run

**Ominaisuudet**

- Rekisteröityminen ja kirjautuminen CSRF-suojauksella

- Muistiinpanojen ja vastausten luominen, muokkaaminen ja poistaminen

- Avainsanahaku

- Yksi tykkäys/ei-tykkäys per käyttäjä per muistiinpano

- Luokat ja käyttäjäprofiilin tilastot

- Sivuittaminen ja suorituskykyindeksit

 **Suorituskykytestaus**

Luotiin 10 000 muistiinpanoa ja 50 000 vastausta:

10 000 muistiinpanoa lisätty: 3,45 s

50 000 vastausta lisätty: 7,82 s

Etusivun latausaika (lämmin välimuisti): < 50 ms
Haun “lorem” suoritus: ~ 120 ms
