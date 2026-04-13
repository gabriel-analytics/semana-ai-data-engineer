Create src/day1/test_models.py that imports the models from src/day1/models.py and tests:
1. Create a valid Order and print it
2. Try Order with qty=0 — should fail
3. Try Order with payment='dinheiro' — should fail
4. Create a valid Review with rating=5 and print it
5. Try Review with rating=6 — should fail

Catch each ValidationError and print the error message. Then run the script.
