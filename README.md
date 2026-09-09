# Tourist Trap vs. Hidden Gem

## A Knowledge Graph for Authentic Urban Discovery

### Project Overview

Most travel platforms recommend the same popular and crowded places, making it difficult for visitors to discover venues that locals actually prefer. This project develops a Knowledge Graph (KG) for authentic urban discovery that distinguishes potential **tourist traps** from **local favourites** and provides more transparent and personalised venue recommendations.

Unlike traditional recommendation systems that mainly rely on popularity rankings, the project combines multiple signals—such as location, venue type, price, proximity to tourist areas, venue history, and seasonality—to model relationships between venues, districts, landmarks, and user preferences.

## Problem Statement

Can simple features such as location, type, price, and proximity to tourist areas be used to identify whether a place is more likely to be a tourist trap or a local favourite?

Most existing travel recommendation systems focus heavily on popularity and do not capture deeper relationships between:

- Venues and neighbourhoods
- Venues and tourist areas
- Pricing and local context
- Venue characteristics and visitor behaviour
- User preferences and venue recommendations

A Knowledge Graph provides a structured way to represent these relationships and use them for both explainable classification and personalised recommendations.

## Proposed Solution

The project combines two approaches:

1. **Rule-based Knowledge Graph reasoning**
2. **Knowledge Graph embeddings**

A set of Datalog rules is used to classify venues as tourist traps or local favourites based on available venue and geographic attributes. These classifications are then added back into the Knowledge Graph as structured information.

The enriched graph is used to train an embedding model, specifically **TransE via PyKEEN**, to capture additional patterns and relationships that may not be explicitly represented by the rules.

This hybrid approach aims to provide:

- Explainable venue classifications
- More personalised recommendations
- Recommendations beyond simple popularity rankings
- Discovery of less obvious relationships between venues and urban areas

## Data Sources

The project will combine data from the following sources:

- **OpenStreetMap** — venue and geographic attributes
- **Foursquare OS Places** — additional venue information
- **data.gv.at** — district demographics and tourist density
- **Austrian tourism statistics** — tourism-related contextual information

## Knowledge Graph Design

### Entity Types

The Knowledge Graph will include the following main entities:

- `Venue`
- `District`
- `City`
- `LandmarkZone`

### Relations

Example relationships include:

- `located_in`
- `priced_relative_to`
- `adjacent_to`
- `classified_as`

These entities and relations will model the urban environment and provide the foundation for logical reasoning and embedding-based recommendations.

## Methodology

### 1. Data Acquisition

Collect venue attributes from OpenStreetMap and Foursquare OS Places, together with district demographics and tourist density information from Austrian open data sources.

### 2. Knowledge Graph Construction

Define the entity types and relationships and load the collected data into a graph structure.

### 3. Logical Classification

Implement a small set of Datalog rules to classify venues as:

- Tourist traps
- Local favourites

The resulting classification labels will be added to the Knowledge Graph.

### 4. Knowledge Graph Embeddings

Train a TransE embedding model using PyKEEN on the annotated Knowledge Graph.

The embedding model will be used to identify hidden patterns and support personalised venue recommendations.

### 5. Knowledge Graph Evolution

Evaluate how venue classifications can be incrementally updated when new information, such as seasonal data, becomes available.

## Project Scope

The initial project focuses on:

- **Vienna** as the primary city
- **Prague or Budapest** as one comparison city

The project is intentionally limited to a manageable prototype scope:

- 6–8 Datalog rules
- A standard TransE model implemented with PyKEEN
- Selected open datasets
- No production deployment
- Multi-city expansion reserved for future work

## Technology Stack

The expected technologies and frameworks include:

- Python
- Knowledge Graph technologies / graph store
- Datalog for rule-based reasoning
- PyKEEN
- TransE
- OpenStreetMap data
- Foursquare OS Places data

## Expected Outcomes

The project aims to demonstrate that combining symbolic reasoning with Knowledge Graph embeddings can improve urban venue discovery.

Expected outcomes include:

- A structured Knowledge Graph of venues, districts, cities, and tourist areas
- Explainable tourist trap and local favourite classifications
- A set of Datalog-based classification rules
- A trained TransE embedding model
- Personalised venue recommendations
- An evaluation of incremental graph updates using seasonal data

## Future Work

Possible future extensions include:

- Expanding the system to additional cities
- Adding more detailed user preference modelling
- Incorporating additional data sources
- Using more advanced Knowledge Graph embedding models
- Developing a production-ready recommendation interface
- Evaluating recommendation quality with user studies

## Project Author

**Khrystyna Vasko**

Student ID: `12307779`

## License

This project is developed for academic purposes.
