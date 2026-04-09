CREATE DATABASE ValentinesGarageDB;
USE ValentinesGarageDB;

CREATE TABLE Employees (
    EmployeeID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100) NOT NULL,
    Role NVARCHAR(50) NOT NULL
);

CREATE TABLE Trucks (
    TruckID INT IDENTITY(1,1) PRIMARY KEY,
    RegistrationNumber NVARCHAR(50) NOT NULL,
    Model NVARCHAR(100) NOT NULL,
    Mileage INT NOT NULL,
    ConditionReport NVARCHAR(MAX),
    Notes NVARCHAR(MAX),
    CheckInDate DATETIME NOT NULL DEFAULT GETDATE()
);

CREATE TABLE RepairTasks (
    TaskID INT IDENTITY(1,1) PRIMARY KEY,
    TruckID INT NOT NULL,
    Description NVARCHAR(255) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending',
    EmployeeID INT NOT NULL,
    TaskNotes NVARCHAR(MAX),
    DateWorkedOn DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_Task_Truck FOREIGN KEY (TruckID)
        REFERENCES Trucks(TruckID),

    CONSTRAINT FK_Task_Employee FOREIGN KEY (EmployeeID)
        REFERENCES Employees(EmployeeID)
);

INSERT INTO Employees (FullName, Role)
VALUES 
('John Smith', 'Mechanic'),
('Sarah Brown', 'Mechanic'),
('Valentine', 'Manager');

SELECT * FROM Trucks;

SELECT * FROM Trucks;

SELECT * FROM Employees;

SELECT * FROM RepairTasks;

SELECT * FROM RepairTasks;

ALTER TABLE RepairTasks

ADD MechanicTaskNotes NVARCHAR(MAX);
SELECT FullName, Role FROM Employees;
ALTER TABLE Employees
ADD Password NVARCHAR(100) NOT NULL DEFAULT 'pass123';
SELECT EmployeeID, FullName, Role, Password
FROM Employees;
INSERT INTO Employees (FullName, Role, Password)
VALUES
('John Albertus', 'Mechanic', 'pass123'),
('Adonis Van Lieverzhen', 'Mechanic', 'pass123');

SELECT COLUMN_NAME, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'RepairTasks';
SELECT * FROM Trucks;
EXEC sp_help 'RepairTasks';

SELECT
    E.FullName,
    T.RegistrationNumber,
    R.Description,
    R.TaskNotes,
    R.Status
FROM RepairTasks R
JOIN Employees E ON R.EmployeeID = E.EmployeeID
JOIN Trucks T ON R.TruckID = T.TruckID;
INSERT INTO Trucks
(RegistrationNumber, Model, Mileage, ConditionReport, Notes)
VALUES
('TRK‑001', 'Volvo FH', 245000, 'Good', 'Regular service required'),
('TRK‑002', 'Scania R500', 312400, 'Fair', 'Brake inspection needed'),
('TRK‑003', 'MAN TGX', 198750, 'Excellent', 'Recently serviced'),
('TRK‑004', 'Mercedes‑Benz Actros', 402100, 'Poor', 'Engine noise reported'),
('TRK‑005', 'DAF XF', 275600, 'Needs Immediate Attention', 'Oil leakage observed');

SELECT TruckID, RegistrationNumber, Model, Mileage, ConditionReport
FROM Trucks;