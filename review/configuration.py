# pylint: disable=import-error
'''
Constants are stored here for use in other parts of the XBlock.
'''
from __future__ import absolute_import
from django.conf import settings

# Needed for review.py #
# Eventually, this should be part of the XBlock fields as a Boolean
SHOW_PROBLEMS = set([
    # This is here for testing purposes. Do not remove
    'DillonX/DAD101x/3T2017',
    # Anant's course
    'course-v1:MITx+6.002.3x_1+2T2016',
    # Quantum Information Science, Part 1
    'course-v1:MITx+8.370.1x+1T2018',
    # Quantum Information Science, Part 2
    'course-v1:MITx+8.370.2x+1T2018',
    # Quantum Information Science, Part 3
    'course-v1:MITx+8.370.3x+1T2018',
])
SHOW_VERTICAL = set([
])

# Needed for get_review_ids.py #
'''
The mappings here are necessary to grab the review content from a review
version of the course (a copy where problems are not graded and have
unlimited attempts).
When accessed, the key is the course the learner is currently interacting
with and the value is the corresponding review course.
'''
REVIEW_COURSE_MAPPING = {
    # Course used for testing. DO NOT REMOVE
    'DillonX/DAD101x/3T2017': 'DillonX/DAD101x_review/3T2017',
    # Anant's course
    'course-v1:MITx+6.002.3x_1+2T2016': 'MITx+6.002.3x_1_review+2T2016',
    # Quantum Information Science, Part 1
    'course-v1:MITx+8.370.1x+1T2018': 'MITx+8.370.1x_review+1T2018',
    # Quantum Information Science, Part 2
    'course-v1:MITx+8.370.2x+1T2018': 'MITx+8.370.2x_review+1T2018',
    # Quantum Information Science, Part 3
    'course-v1:MITx+8.370.3x+1T2018': 'MITx+8.370.3x_review+1T2018',
}
ENROLLMENT_COURSE_MAPPING = {
    # Course used for testing. DO NOT REMOVE
    'DillonX/DAD101x/3T2017': 'DillonX/DAD101x_review/3T2017',
    # Anant's course
    'course-v1:MITx+6.002.3x_1+2T2016': 'course-v1:MITx+6.002.3x_1_review+2T2016',
    # Quantum Information Science, Part 1
    'course-v1:MITx+8.370.1x+1T2018': 'course-v1:MITx+8.370.1x_review+1T2018',
    # Quantum Information Science, Part 2
    'course-v1:MITx+8.370.2x+1T2018': 'course-v1:MITx+8.370.2x_review+1T2018',
    # Quantum Information Science, Part 3
    'course-v1:MITx+8.370.3x+1T2018': 'course-v1:MITx+8.370.3x_review+1T2018',
}
XBLOCK_VIEW_URL_TEMPLATE = settings.LMS_ROOT_URL + '/xblock/block-v1:{course_id}+type@{type}+block@{xblock_id}'
