#import db_actions

from bpf import classes

@classes.func_logger
def parse_canvas(canvas_list):
    """
Most on the information about the individual canvases is standardised, so there can be a module used to extract it from all.
Only the label of the canvas can hold different kinds of information and hence has to be dissected individually later.
    """
    images = []
    i = 0
    for canvas in canvas_list:

        i = i+1
        im = classes.Image()
        im.index = i
        im.label_raw = canvas["label"]
        im.baseurl = canvas["images"][0]["resource"]["service"]["@id"]
        im.width = canvas["images"][0]["resource"]["width"]
        im.height = canvas["images"][0]["resource"]["height"]
        images.append(im)
    return images

@classes.func_logger
def parse_canvas_yale(canvas_list):
    """
Most on the information about the individual canvases is standardised, so there can be a module used to extract it from all.
Only the label of the canvas can hold different kinds of information and hence has to be dissected individually later.

This variant is used for books from Yale, where the label is not "label' but ["label"]["none"][0]. I keep it here,
in case any other library uses a similar strange system
    """
    images = []
    i = 0
    for canvas in canvas_list:

        i = i+1
        im = classes.Image()
        im.index = i
        im.label_raw = canvas["label"]["none"][0]
        im.baseurl = canvas["items"][0]["items"][0]["body"]["service"][0]["@id"]
        im.width = canvas["items"][0]["items"][0]["body"]["width"]
        im.height = canvas["items"][0]["items"][0]["body"]["height"]
        images.append(im)
    return images