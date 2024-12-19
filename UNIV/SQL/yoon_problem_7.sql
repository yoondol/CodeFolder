SELECT E.Fname, E.Lname
FROM EMPLOYEE E
JOIN WORKS_ON W
ON E.Ssn = W.Essn
WHERE W.Pno = (
    SELECT P.Pnumber
    FROM PROJECT P
    WHERE P.Pname = 'ProductX'
) AND W.Hours > 10

SELECT E.Fname, E.Lname
FROM EMPLOYEE AS E
JOIN DEPENDENT DE
ON E.Ssn = DE.Essn
WHERE DE.Dependent_name = E.Fname

SELECT E.Fname, E.Lname
FROM EMPLOYEE AS E
WHERE E.Super_ssn = (
    SELECT S.ssn
    FROM EMPLOYEE S
    WHERE S.Fname = 'Franklin' AND S.Lname = 'Wong'
)
