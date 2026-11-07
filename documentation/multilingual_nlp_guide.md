# Multilingual NLP Command Guide

This document describes how natural language commands are recognized, normalized, and executed in **English**, **Hindi (Devanagari & Hinglish)**, **Marathi (Devanagari & Marathi-English)**, and **Code-Mixed** dialects.

---

## 1. Supported Languages and Markers

| Language | Script | Identification Strategy | Sample Commands |
| :--- | :--- | :--- | :--- |
| **English** | Latin | English token patterns, standard verbs (`create`, `show`, `compare`, `filter`) | `Create a bar chart of monthly sales`<br>`Show total revenue`<br>`Compare sales by region` |
| **Hindi (Devanagari)** | Devanagari (`\u0900-\u097F`) | Distinct Hindi markers: `बनाओ`, `दिखाओ`, `करो`, `में`, `का`, `की`, `कुल`, `हटाओ` | `मासिक बिक्री का बार चार्ट बनाओ`<br>`कुल राजस्व दिखाओ`<br>`क्षेत्र के अनुसार बिक्री की तुलना करो` |
| **Hinglish** | Latin | Hindi grammar transliterated to Latin: `banao`, `dikhao`, `karo`, `badlo`, `mein`, `ka` | `Monthly sales ka bar chart banao`<br>`Total revenue dikhao`<br>`Revenue chart ko line chart mein change karo` |
| **Marathi (Devanagari)** | Devanagari (`\u0900-\u097F`) | Distinct Marathi markers: `करा`, `दाखवा`, `बदला`, `तयार करा`, `एकूण`, `मधील`, `नुसार`, `कमी`, `जास्त` | `मासिक विक्रीचा बार चार्ट तयार करा`<br>`एकूण महसूल दाखवा`<br>`विभागानुसार विक्रीची तुलना करा` |
| **Marathi-English** | Latin | Marathi grammar transliterated to Latin: `tayar kara`, `dakhva`, `badla`, `ekun`, `nusar`, `madhe`, `cha` | `Monthly sales cha bar chart tayar kara`<br>`Ekun revenue dakhva`<br>`Region nusar sales compare kara`<br>`Sales chart line chart madhe badla` |

---

## 2. Multilingual Vocabulary Normalization

### 2.1 Visualizations (Chart Types)
- **Bar Chart**: `bar chart`, `bar`, `स्तंभ आलेख`, `बार चार्ट`, `aadva bar` (horizontal)
- **Line Chart**: `line chart`, `line`, `रेषा आलेख`, `रेखा चार्ट`, `लाइन`
- **Pie Chart**: `pie chart`, `pie`, `वृत्तालेख`, `पाई चार्ट`
- **Donut Chart**: `donut`, `doughnut`, `डोनट चार्ट`
- **Scatter Plot**: `scatter`, `scatter plot`, `बिंदू आलेख`, `स्कैटर`
- **Area Chart**: `area chart`, `area`, `क्षेत्र आलेख`, `एरिया`
- **Histogram**: `histogram`, `hist`, `हिस्टोग्राम`
- **Box Plot**: `box plot`, `box`, `बॉक्स प्लॉट`

### 2.2 Aggregation Terms
- **Sum / Total**: `total`, `sum`, `कुल`, `एकूण`, `ekun`, `kul`, `jod`, `बेरीज`, `berij`
- **Average**: `average`, `avg`, `mean`, `औसत`, `सरासरी`, `ausat`, `sarasari`
- **Count**: `count`, `orders`, `total orders`, `संख्या`, `गिनती`, `sankhya`, `ginti`, `moza`
- **Minimum**: `minimum`, `min`, `lowest`, `न्यूनतम`, `कमीत कमी`, `kamit kami`, `sabse kam`, `sarvat kami`
- **Maximum**: `maximum`, `max`, `highest`, `अधिकतम`, `जास्तीत जास्त`, `sabse jyada`, `sarvat jast`

### 2.3 Time Dimensions
- **Monthly**: `monthly`, `month`, `मासिक`, `महिना`, `महीना`, `mahina`, `mahinyacha`
- **Yearly**: `yearly`, `annual`, `वार्षिक`, `वर्ष`, `साल`, `varsha`, `varshik`
- **Quarterly**: `quarterly`, `त्रैमासिक`, `quarter`
- **Daily**: `daily`, `दैनिक`, `रोज`, `roj`, `din`

---

## 3. Context Awareness & Pronouns

When a user says:
- `Change it to a pie chart`
- `Revenue chart ko line chart mein change karo`
- `त्या चार्टला लाइन चार्ट मध्ये बदला` (Change that chart to line chart)
- `Filter it for the top 5`

The system:
1. Checks if a chart was explicitly named or selected.
2. If pronouns (`it`, `that`, `use`, `isko`, `tyala`) are used, resolves to the **most recently created or modified chart** in session memory.
3. Keeps all existing charts intact on the dashboard.

---

## 4. Ambiguity Resolution Workflow

When a command lacks essential parameters:
- **Missing Metric**:
  - User: `Show the top five`
  - System: `Top 5 based on which metric: Sales, Profit, Quantity?` (displays interactive option buttons)
  - User: clicks `Sales` or types `Sales`
  - System: Resumes execution and displays the Top 5 items based on Sales.
- **Unclear Target Chart**:
  - User: `Change that chart` (with multiple charts present and none currently selected)
  - System: `Which chart would you like to modify?` (displays list of existing chart titles)
