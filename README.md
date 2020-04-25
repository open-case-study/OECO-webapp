Open European Case study Observatory - plan & front end
=======================================================

![OECO_logo](./design/logo_OECO.png)

General project description on [devpost](https://devpost.com/software/open-european-case-study-observatory).

Visual overview of the structure
--------------------------------

1. [Bird's eye view of project](./design/overview.pdf)
2. [Front page sketch](https://test.opencasestudy.eu)
3. [Submission sketch](https://test.opencasestudy.eu/icd10_search_test.html)
4. [Search case sketch](./design/overview_search_case.pdf)
5. API Big tada page sketch
6. [Database overview](./design/overview_database.pdf)

Input needed
------------

* legal: when is data anonimous enough?
Discussion of dabase and privacy is in Google docs folder

Tasks
-----

STRUCTURE

* agree on input data required - done
* agree which data should be indexed for quick queries - done
* agree on user registration
* agree on structure of database - done
* agree on structure of JSON exchanged between front end and back end
* agree on general layout -done

FUNCTIONALITY

* landing page - done
* front end input form  --- data input +  - done
* front end retrival form (for medical doctors) - partially done
* front end retrival info (for data scientists)
* back end - database
* back end - queries from front end

FEEL

* front end input form  --- make good design
* front end retrival form (for medical doctors) --- make good design


Building blocks needed
----------------------

We need discrete inputs to ensure that data entered into the database is normalised (and hence machine searchable).

Everything on one place (at least with US approved drugs)
https://clinicaltables.nlm.nih.gov/ 

Autocompleters [API documentation](https://lhncbc.github.io/autocomplete-lhc/docs.html)
Autocompleter [demo page](https://lhncbc.github.io/autocomplete-lhc/) and [code page](https://github.com/lhncbc/autocomplete-lhc)

* javascript for finding codes in International Classification of Disease (ICD10)
 -- datasource via rest api: https://clinicaltables.nlm.nih.gov/apidoc/conditions/v3/doc.html (autocomplete search for conditions, including synonims, providing ICD10 and ICD9 codes)
 -- datasource WHO https://icd.who.int/icdapi/docs2/icd11ect-1.2/  and  https://icd.who.int/icdapi 
* javascript for finding normalised drug names
 -- data source: https://melclass.edqm.eu/prescriptions/list_medicines 
  
