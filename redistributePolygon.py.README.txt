# README

## Note
The last known working version of this tool is in
O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report
Catchments\UpperRoss\redistributePolygon.py

Before being used, the Issues section should be read and understood.  The
Issues section and instructions on use can be found inside the
redistributedPolygon.py file itself. These can be read by opening the
redistributedPolygon.py in a text editor.

## Problems

On 20170926 I had to rerun the model. I found the following problems:
- growth model output used as inputs were not the same as the original GM
  outputs (this is because the latest GM results were moderated for the LGIP).
  The .csv file had problems:
  1. some of the values were strings (ie, had commas, and had quotes around
     them).
  2. even when the above seemed to be corected, the fields of the feature
     class were text once the csv was joined.
- The code was horrible to follow. It was all over the place and very hard to
  follow.
- The code was writting with the intention of converting it into an arcpy
  tool, which meant it was very hard to debug.

## lessons learned

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
