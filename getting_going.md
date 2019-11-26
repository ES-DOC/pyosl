
### Instructions for playing with code

Note you need a schema to play with at the moment, it wont boot ab initio as a tool.

Right, let's get going:

- You've got anaconda
- You've got git
- git clone repo pyosl from bitbucket address
    - oh, you have a credential problem?
    - copy your key pair into your ssh directory.
- ```pip install .```
- try it:   
- 
```python

	  >>>import pysol
      ...
      ValueError: Attempt to load ontology from non-existent folder!

```
-  Yes, you need to load the ontology too!
- git clone repo esdoc-schema: ```git clone https://github.com/bnlawrence/esdoc-cim-v2-schema.git```
- Configure pyosl to see that ... for now there is a bug which means you need to edit the config file inside the distribution and re-install it.  
- 
```python

       >>> import pyosl
       >>>
```
- Bingo
