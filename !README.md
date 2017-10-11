
## lessons learned reviewing old code:

### Unit tests are paramount
Unit tests would have picked up some of these issues. For future scripts,
start with unit tests. Take a subset of the real data by creating a testing
shapefile, then clip all the data to that file, eg,
```
if testing:
    for layer in input_layers:
      Clip_analysis (in_features, clip_features, out_feature_class, {cluster_tolerance})
```

### input data format should be checked
Parse csv files to make sure they as expected. Check the class of fields to
see that they are as expected.

### Put all variable declarations into some sort of setup function

### lint the code

### Create a log() method 
This function will print(), logging.info(), or arcpy.AddMessages()
depending on how it's run.

### put code blocks into variable
This will keep folds working and increase readability.
