create database healthcare;
use healthcare;

create table Diagnoses(
DiagnosisID int primary key,
DiagnosisName varchar(255)
);

create table Outcomes(
OutcomeID int primary key,
OutcomeName varchar(255)
);

create table Patients(
PatientID int primary key,
Name varchar(255),
Age int,
Gender char(1),
DiagnosisID int,
AdmissionDate Date,
DischargeDate date,
OutcomeID int,
TreatmentCost decimal(10,2),
foreign key (DiagnosisID) references Diagnoses(DiagnosisID),
foreign key (OutcomeID) references Outcomes(OutcomeID)
);

create table Labs(
LabID int primary key,
PatientID int,
TestName varchar(255),
Result Decimal(10,2),
NormalRange varchar(255),
foreign key (PatientID) references Patients(PatientID)
);
 
select * from Patients;
select * from Diagnoses;
select * from Labs;
select * from Outcomes;

-- retrieve patient lab history

select p.patientID,p.name,d.diagnosisname,o.outcomename,l.testname,l.result,l.Normalrange
from patients p
join diagnoses d on p.diagnosisID=d.diagnosisID
join outcomes o on p.outcomeID = o.outcomeID
join labs l on p.patientID = l.patientID
order by p.patientID, l.testname;

-- avg lab results by diagnosis

select d.diagnosisname, l.testname, avg(l.result) as AVGResult
from patients p
join diagnoses d on p.diagnosisID = d.diagnosisID
join labs l on p.patientid = l.patientid
group by diagnosisname , l.testname;

-- count abnormal result

select p.patientid, p.name, count(*) as AbnormalCount
from patients p 
join labs l on p.patientid = l.patientid
where (l.testname = 'Blood Sugar' and l.result>120) or
( l.testname ='Cholestrol' and l.result>200) or
( l.testname ='Hemoglobin' and l.result<13)
group by p.patientid, p.name
order by AbnormalCount desc; 

-- diagnosis with highest treatment cost

select d.diagnosisname, sum(treatmentcost) as TotalCost
from patients p 
join diagnoses d on p.diagnosisid = d.diagnosisid 
group by d.diagnosisname
order by TotalCost desc;

-- patient at risk by age and gender

select p.patientid , p.name , p.age, d.diagnosisname, o.outcomename
from patients p 
join diagnoses d on p.diagnosisid = d.diagnosisid
join outcomes o on p.outcomeid = o.outcomeid
where p.age > 65 and o.outcomename != 'Recovered';

-- lab trend over time for specific patient

select l.testname , l.result, p.admissiondate
from labs l
join patients p on l.patientid = p.patientid
where p.patientid in (2,4,6,8,10,12)
order by p.admissiondate;

-- distribution of outcome by diagnosis

select d.diagnosisname, o.outcomename, count(*) as OutcomeCount
from patients p
join diagnoses d on p.diagnosisid = d.diagnosisid
join outcomes o on p.outcomeid = p.outcomeid
group by d.diagnosisname, o.outcomename
order by d.diagnosisname, o.outcomename desc;
