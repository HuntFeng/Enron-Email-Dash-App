# File structures
## app.py
This is a dash_based web app.
The app uses dash to start server and display stuff. Most of the calculations are done by graph_tool and pandas. There are two main parts in this app:
1. Graph analysis: displaying a list of interesting people using different ranking algorithms. Two nicely rendered graph helps users to grasp their roles in the comapny.
2. Email browser: allowing uers to search emails between two specific people. A nice interactive graph will show emails and average sentiment between the chosen two people. 

## enron_emails_dataframe.pickle
This is the pandas dataframe of all emails. The structure of the dataframe is shown below:

    index   date    from       to        subject    sentavg 
      0     xxxx     A       [B,C,D]     xxxxxxx      -1~1

If the sentiment is closer to -1, means it is associated more with bad emitions such as anger, upset. If the sentiment is closer to 1, then it means it is associated more with good emotions such as happy. 0 means neutral.

## enron_emails_graph.xml.gz
This is the social network of the company staff, no customers in this network. People are vertices in this graph, and if two people in this company has communications(they talk via emails), there will be an edge joining them. There are no parallel edges. The graph information is listed below: 
* number of vertieces: 32597, number of edges: 201458.
* vertex property: email address.
* no parallel edges.


## le_classes.npy
This is the for the transformation between vertex index and person's email.

```python
import numpy as np
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
le.classes_ = np.load("le_classes")

# transform takes a list of email address, and return their corresponding vertex index.
le.transform(["billy.lemmons@enron.com", "jeff.skilling@enron.com"])  # output: [ 3295, 15235]

# inverse_transform takes a list of indices, and return their corresponding email address.
le.inverse_transform([0,1]) # output: ['"dfranklin@hanovermeasurement.com" <.lwbthemarine@enron.com>', '"mr." <.robin@enron.com>']
```