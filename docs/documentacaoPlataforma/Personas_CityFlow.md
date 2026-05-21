# Personas and Use Cases (CityFlow)

Based on the differentiating features of the **CityFlow** application and the socio-demographic analysis of the target audiences of the Human-Computer Interaction (HCI) course, the following Personas represent the critical users (edge cases) around which the interface and the mapping algorithm were built.

| Name / Age | Main limitation (Profile) | Primary need on CityFlow | Common frustration with mainstream maps (Google Maps / Apple Maps) |
| :--- | :--- | :--- | :--- |
| **João**, 34 | **Motor:** Wheelchair user (manual). | Routes with controlled slope and strict avoidance of pavements without lowered curbs, stairs, and loose ground. | Mainstream maps send him through the "fastest" path. That path often hides a steep hill that exhausts him, or it pushes him into ancient cobblestone he cannot ride over — he ends up turning back and wasting energy. |
| **Maria**, 72 | **Sensory (reduced vision) and physical (fatigue):** Elderly with partial cataracts who walks with a cane. | Navigate with an *Easy-Read* mode (clean interface), large-scale buttons, and prioritise flat distances that require little respiratory effort. | The interface is cluttered with irrelevant information (restaurants, hotels). The font is tiny. The maps never warn her about pavement works (no crowdsourcing) which force her to take risks on the road. |
| **Ricardo**, 45 | **Cognitive-sensory:** Colour-blind (Deuteranopia — difficulty in the green/red axis). | Read the map through dynamic contrast, obvious visual patterns or haptic feedback (vibration) when he turns the wrong way. | Red route lines on a green topography blend together. He cannot tell at a glance which is a fast lane and which is a secondary pedestrian street. Multimodal warnings about alternate routes are missing. |

These Personas reinforce the existence of the variables `max_incline`, `avoid_stairs` and the *Easy-Read* mode, plus the crowdsourcing feature for in-road obstacles, which form the foundations of CityFlow.
