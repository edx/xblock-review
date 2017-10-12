'''
Description
'''

import logging

from courseware.models import StudentModule
from opaque_keys.edx.locator import CourseLocator
from opaque_keys.edx.keys import UsageKey
from enrollment.api import get_enrollment, add_enrollment, update_enrollment
from lms.djangoapps.course_blocks.api import get_course_blocks
from xmodule.modulestore.django import modulestore
import crum
import random
import json

log = logging.getLogger(__name__)

REVIEW_COURSE_MAPPING = {
    # Sandbox
    'course-v1:DillonX+DAD301+2017_T3': 'DillonX+DAD302+2017_T3',
    # Sandbox demo Anant's course
    'course-v1:MITx+6.002.3x+2T2016': 'MITx+6.002.3rx+2T2016',
    # Sandbox demo Simona's course
    'course-v1:MITx+2.01x+3T2017': 'MITx+2.01rx+3T2017',
}
ENROLLMENT_COURSE_MAPPING = {
    # Sandbox
    'course-v1:DillonX+DAD301+2017_T3': 'course-v1:DillonX+DAD302+2017_T3',
    # Sandbox demo Anant's course
    'course-v1:MITx+6.002.3x+2T2016': 'course-v1:MITx+6.002.3rx+2T2016',
    # Sandbox demo Simona's course
    'course-v1:MITx+2.01x+3T2017': 'course-v1:MITx+2.01rx+3T2017',
}
TEMPLATE_URL = 'https://dillon-demo.sandbox.edx.org/xblock/block-v1:{course_id}+type@{type}+block@{xblock_id}'


def get_problems(num_desired, current_course):
    '''
    Doc String
    Returns a list of num_desired tuples in the form (URL to display, correctness, attempts)
    '''
    log.critical("********** get_problems *************")
    log.critical(TEMPLATE_URL)
    user = crum.get_current_user()

    enroll_user(user, current_course)
    
    problem_data = []
    # Each record corresponds to a problem the user has loaded
    # in the original course
    for record in StudentModule.objects.filter(**{'student_id': user.id, 'course_id': current_course, 'module_type': 'problem'}):
        # record.module_state_key takes the form: 
        # block-v1:{course_id}+type@problem+block@{problem_id}
        problem_id = str(record.module_state_key).split("@")[-1]

        # Actual logic regarding the record should go here
        state = json.loads(record.state)

        # The key 'selected' shows up if a problem comes from a
        # library content module. These cause issues so we skip this.
        # Issue: Library content contains problems but the CSM brings up
        # the library content and not the problems within
        if 'selected' in state:
            continue

        correctness, attempts = get_correctness_and_attempts(state)

        # if not is_correct_review_problem(user, current_course, problem_id):
        #     problem_data.append(problem_id)
        problem_data.append((problem_id, correctness, attempts))

    if len(problem_data) < num_desired:
        return []

    problems_to_show = random.sample(problem_data, num_desired)
    review_course_id = REVIEW_COURSE_MAPPING[str(current_course)]
    urls = []
    for problem, correctness, attempts in problems_to_show:
        urls.append((TEMPLATE_URL.format(course_id=review_course_id,
                    type='problem', xblock_id=problem), correctness, attempts))
    return urls

def get_vertical(current_course):
    '''
    Doc String. The vertical will contain 1 or more problems
    Returns a vertical id (str) to render for review.
    '''
    user = crum.get_current_user()

    enroll_user(user, current_course)

    store = modulestore()
    course_usage_key = store.make_course_usage_key(current_course)
    course_blocks = get_course_blocks(user, course_usage_key)

    vertical_data = set()

    # Each record corresponds to a problem the user has loaded
    # in the original course
    for record in StudentModule.objects.filter(**{'student_id': user.id, 'course_id': current_course, 'module_type': 'problem'}):
        # record.module_state_key takes the form:
        # block-v1:{course_id}+type@problem+block@{problem_id}
        problem_id = str(record.module_state_key).split("@")[-1]

        # Actual logic regarding the record should go here
        state = json.loads(record.state)

        # The key 'selected' shows up if a problem comes from a
        # library content module. These cause issues so we skip this.
        # Issue: Library content contains problems but the CSM brings up
        # the library content and not the problems within
        if 'selected' in state:
            continue

        # parent takes the form: block-v1:{course_id}+type@vertical+block@{vertical_id}
        parent = course_blocks.get_parents(record.module_state_key)[0]
        vertical_id = str(parent).split("@")[-1]

        # correctness, attempts = get_correctness_and_attempts(state)

        # if not is_correct_review_problem(user, current_course, problem_id):
        #     vertical_data.append(parent)
        vertical_data.add(vertical_id)

    if len(vertical_data) < 1:
        return []

    vertical_to_show = random.sample(vertical_data, 1)[0]
    review_course_id = REVIEW_COURSE_MAPPING[str(current_course)]
    return (TEMPLATE_URL.format(course_id=review_course_id,
                    type='vertical', xblock_id=vertical_to_show))

def enroll_user(user, current_course):
    '''
    If the user is not enrolled in the review version of the course,
    they are unable to see any of the problems. This ensures they
    are enrolled so they can see review problems.
    '''
    enrollment_course_id = ENROLLMENT_COURSE_MAPPING[str(current_course)]
    enrollment_status = get_enrollment(user.username, enrollment_course_id)
    if not enrollment_status:
        add_enrollment(user.username, enrollment_course_id)
    elif not enrollment_status['is_active']:
        update_enrollment(user.username, enrollment_course_id, is_active=True)

def delete_state_of_review_problem(user, current_course, problem_id):
    '''
    Deletes the state of a review problem so it can be used infinitely
    many times.
    '''
    pass

def is_correct_review_problem(user, current_course, problem_id):
    '''
    Checks a review problem to see if the learner has already correctly
    answered it.

    Returns True if the review problem was correctly answered, False otherwise
    Catches IndexError if learner has never seen the review problem before.
    Catches KeyError if learner has never attempted the review problem before.
    '''
    try:
        review_record = StudentModule.objects.filter(**{'student_id': user.id,
            'module_state_key': UsageKey.from_string(
                'block-v1:'+REVIEW_COURSE_MAPPING[str(current_course)]+
                '+type@problem+block@'+problem_id)})[0]
        review_record_state = json.loads(review_record.state)
        for key in review_record_state["correct_map"].keys():
            # If any part of a problem was incorrect,
            # it is eligible to be shown again
            if review_record_state["correct_map"][key]["correctness"] != 'correct':
                return False
        return True
    except (IndexError, KeyError):
        return False

def get_correctness_and_attempts(state):
    '''
    Input: state of a problem

    Returns a tuple of (correctness, attempts)
        correctness (str): 'correct' or 'incorrect'
        attempts (int): 0 if never attempted, else number of times attempted
    Catches KeyError if learner never attempted the problem
    '''
    if state['score']['raw_earned'] == state['score']['raw_possible']:
        correctness = 'correct'
    else:
        correctness = 'incorrect'
    if 'attempts' in state:
        attempts = state['attempts']
    else:
        attempts = 0
    # try:
    #     attempts = state['attempts']
    # except KeyError:
    #     attempts = 0
    return (correctness, attempts)
