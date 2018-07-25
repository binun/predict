for %%P in (dow) do (
echo %%P

java -jar online.jar %%P hist
java -jar online.jar %%P last
python Main.py %%P_csv
java -jar online.jar %%P mail
)