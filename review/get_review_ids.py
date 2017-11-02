'''
The logic for actually grabbing review content is contained here for the
Review xBlock. This works by having a copy of the actual course a learner
is interacting with that is hidden from learners. This copied course hosts
the content we will show as review so the review content displayed has a
fresh state and can be set to ungraded so it doesn't affect the learners'
grades. There are two ways review content can be grabbed:
    On a per problem basis
    On a unit basis (this would be single view that contains multiple problems)
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

import review.configuration

log = logging.getLogger(__name__)

# TODO: Switch to using CourseLocators and/or CourseKeys everywhere


def get_problems(num_desired, current_course):
    '''
    Looks through all the problems a learner has previously loaded and randomly
    selects num_desired of them. Also checks if the learner had originally
    answered it correctly or incorrectly and after how many attempts.

    Parameters:
        num_desired (int): the number of desired problems to show the learner
        current_course (CourseLocator): The course the learner is currently in

    Returns a list of num_desired tuples in the form (URL to display, correctness, attempts)
    '''
    user = crum.get_current_user()

    enroll_user(user, current_course)
    
    problem_data = []
    # Each record corresponds to a problem the user has loaded in the original course
    problem_filter = {'student_id': user.id, 'course_id': current_course, 'module_type': 'problem'}
    for record in StudentModule.objects.filter(**problem_filter):
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
    Looks through all the problems a learner has previously loaded and
    finds their parent vertical. Then randomly selects a single vertical
    to show the learner.

    Parameters:
        current_course (CourseLocator): The course the learner is currently in

    Returns a url (str) with the vertical id to render for review.
    '''
    user = crum.get_current_user()

    enroll_user(user, current_course)

    store = modulestore()
    course_usage_key = store.make_course_usage_key(current_course)
    course_blocks = get_course_blocks(user, course_usage_key)

    vertical_data = set()

    # Each record corresponds to a problem the user has loaded
    # in the original course
    problem_filter = {'student_id': user.id, 'course_id': current_course, 'module_type': 'problem'}
    for record in StudentModule.objects.filter(**problem_filter):
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

        vertical_data.add(vertical_id)
    if not vertical_data:
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

    Parameters:
        user (User): the current user interacting with the review xBlock
        current_course (CourseLocator): The course the learner is currently in
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

    Parameters:
        user (User): the current user interacting with the review xBlock
        current_course (CourseLocator): The course the learner is currently in
        problem_id (str?): The problem id whose state should be cleared
    '''
    pass

def get_correctness_and_attempts(state):
    '''
    From the state of a problem from the Courseware Student Module,
    determine if the learner correctly answered it initially and
    the number of attempts they had for the original problem
    
    Parameter:
        state (dict): The state of a problem

    Returns a tuple of (correctness, attempts)
        correctness (Bool): True if correct, else False
        attempts (int): 0 if never attempted, else number of times attempted
    '''
    if state['score']['raw_earned'] == state['score']['raw_possible']:
        correctness = True
    else:
        correctness = False

    if 'attempts' in state:
        attempts = state['attempts']
    else:
        attempts = 0

    return (correctness, attempts)

def is_correct_review_problem(user, current_course, problem_id):
    '''
    Checks a review problem to see if the learner has already correctly
    answered it.

    Returns True if the review problem was correctly answered, False otherwise
    '''
    try:
        review_problem_usage_key = UsageKey.from_string(
            'block-v1:'+REVIEW_COURSE_MAPPING[str(current_course)]+
            '+type@problem+block@'+problem_id)
        review_problem_filter = {'student_id': user.id, 'module_state_key': review_problem_usage_key}
        review_record = StudentModule.objects.filter(**review_problem_filter)[0]
        review_record_state = json.loads(review_record.state)
        for key in review_record_state["correct_map"]:
            # If any part of a problem was incorrect,
            # it is eligible to be shown again
            if review_record_state["correct_map"][key]["correctness"] != 'correct':
                return False
        return True

    # Catches IndexError if learner has never seen the review problem before.
    # Catches KeyError if learner has never attempted the review problem before.
    except (IndexError, KeyError):
        return False
