# Flask-prosjekt -- Dokumentasjon

## 1. Forside

**Prosjekttittel:** OsloStudent \
**Navn:** Nikita \
**Klasse:** 2IMD \
**Dato:** 19.11.25

**Kort beskrivelse av prosjektet:**\
En nettside for elever ved Osloskolen.

------------------------------------------------------------------------

## 2. Systembeskrivelse

**Formål med nettsiden:**\
En nettside bare for elever ved Osloskolen.

**Brukerflyt:**\
Man logger inn ved bruk av skole e-post, dataen skal lagres inn i en database.

**Teknologier brukt:**

-   Python / Flask
-   Fauna DB
-   HTML / CSS / JS

------------------------------------------------------------------------

## 3. Server-, infrastruktur- og nettverksoppsett

### Servermiljø

Raspberry pi 4 / Ubuntu

### Nettverksoppsett

-   Nettverksdiagram
-   IP-adresser
-   Porter
-   Brannmurregler

Eksempel:

    Klient → Waitress → MariaDB

### Tjenestekonfigurasjon

-   systemctl / Supervisor
-   Filrettigheter
-   Miljøvariabler

------------------------------------------------------------------------

## 4. Prosjektstyring -- GitHub Projects

-   To Do / In Progress / Done
-   Issues
-   Skjermbilde (valgfritt)

Refleksjon: Hvordan hjalp Kanban arbeidet?\
    
    Nå er det mye lettere å følge progresjon av nettsiden

------------------------------------------------------------------------

## 5. Databasebeskrivelse

**Databasenavn:**

    Fauna

**Tabeller:**\
\| Tabell \| Felt \| Datatype \| Beskrivelse \|\
\|--------\|------\|----------\|-------------\|\
\| customers \|  id  \| INT \| Primærnøkkel \|\
\| customers \| name \| VARCHAR(255) \| Navn \|\
\| customers \| address \| VARCHAR(255) \| Adresse \|

**SQL-eksempel:**

``` sql
CREATE TABLE customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  address VARCHAR(255)
);
```

------------------------------------------------------------------------

## 6. Kodeforklaring

Forklar ruter og funksjoner (kort).

------------------------------------------------------------------------

## 7. Sikkerhet og pålitelighet

-   .env\
-   Miljøvariabler\
-   Parameteriserte spørringer\
-   Validering\
-   Feilhåndtering

------------------------------------------------------------------------

## 8. Feilsøking og testing

-   Typiske feil\
-   Hvordan du løste dem\
-   Testmetoder

------------------------------------------------------------------------

## 9. Konklusjon og refleksjon

-   Hva lærte du?\
-   Hva fungerte bra?\
-   Hva ville du gjort annerledes?\
-   Hva var utfordrende?

------------------------------------------------------------------------

## 10. Kildeliste

-   w3schools:\
    https://www.w3schools.com/
-   Fauna:\
    https://docs.faunadb.org/fauna/current/
-   Youtube:
    -   7 Database Paradigms:\
        https://www.youtube.com/watch?v=W2Z7fbCLSTw
    -   FaunaDB Basics - The Database of your Dreams:\
        https://www.youtube.com/watch?v=2CipVwISumA
-   Teams:\
    https://teams.microsoft.com/l/entity/77be3f72-7c14-415f-992c-3511dd54a4ae/classwork?context=%7B%22channelId%22%3A%2219%3Ah7S08vAuVG_6mwoVTLcS2mptEzDELy9ATvgrFmFEvYY1%40thread.tacv2%22%2C%22contextType%22%3A%22channel%22%2C%22subEntityId%22%3A%22%7B%5C%22action%5C%22%3A%5C%22navigate%5C%22%2C%5C%22view%5C%22%3A%5C%22classwork-list%5C%22%2C%5C%22config%5C%22%3A%7B%5C%22classes%5C%22%3A%5B%7B%5C%22id%5C%22%3A%5C%2239aa8592-48c1-41b5-b66f-553b4a7d544e%5C%22%2C%5C%22moduleIds%5C%22%3A%5B%5C%22d5655950-5bd6-470a-9dd8-01eac0aa4891%5C%22%5D%7D%5D%7D%2C%5C%22deeplinkType%5C%22%3A4%7D%22%7D&groupId=39aa8592-48c1-41b5-b66f-553b4a7d544e&tenantId=a5a66368-d49e-4bf5-af9a-6ccbf48e6655&openInMeeting=false&isTeamLevelApp=true