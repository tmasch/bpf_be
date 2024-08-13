"""
Testing of classes
"""
import classes

#def test_frame_


def test_frame_json():
    """ Class Frame, Test of to_json method """
    frame=classes.Frame()
    frame.id="abc"
    s=frame.to_json()
    print(s)
    assert isinstance(s,str)
