Review XBlock
-------------

The Review XBlock displays problems from earlier in the course to learners so they are able to test their understanding of course concepts by retrying these problems.

Long Description
----------------

This repository contains all of the code for the Review XBlock. The Review XBlock is designed to act as a review tool for learners in their edX course. The way it is implemented, the XBlock pulls from all problems a learner has previously loaded in the course and randomly selects 5 of them to reshow the learner. The idea behind reshowing problems the learner has seen is to simulate a review of the concepts the problems should be testing so in retrying the problem, they are reviewing their knowledge of the concept. These review problems contain a fresh state of the problem and are ungraded so learners are able to try them without fear of it harming their grade.

License
-------

The code in this repository is licensed under version 3 of the AGPL
unless otherwise noted. Please see the `LICENSE`_ file for details.

.. _LICENSE: https://github.com/edx/xblock-review/blob/master/LICENSE

How to use
----------

The Review XBlock relies on the creation of a second, almost identical course that hosts the problems that end up being shown to learners. This enables the learner to interact with identical copies of your problems without overwriting any state in your course (such as the original grade they received on a problem). It also allows learners to have unlimited attempts, know the problems are ungraded, and be able to see the answer once they have attempted answering the problem.

In order to use the Review XBlock, first follow the steps listed in `Creating a shadow course for the Review XBlock`_ and then the steps listed in `Adding the Review XBlock to your course`_.

**Note:** The Review XBlock is currently unsupported by edX.

Creating a shadow course for the Review XBlock
----------------------------------------------

At the moment, this process requires coordination with an employee at edX since it involves creating a new course.

1. \* **EdX Employee Required** \* If first time creating the shadow course for the course using the Review XBlock, create the shadow course in Publisher by selecting "Create New Course." If not, skip to step 2.

  \a. The new course should have the same organization as the course that will include the Review XBlock.
  
  \b. The course number **MUST** match the original course's number, but with "_review" appended to the end (e.g. Original course number: "5.555.x", Shadow course number **MUST** be: "5.555.x_review")
  
  \c. The title of the course can be whatever you want, but I have found it helpful to clearly specify it as the secondary course by appending "REVIEW" to the end of the name (e.g. Original course title: "Title of My Course", Shadow course title: "Title of My Course REVIEW").
  
  \d. Select "I want to add a run to this course at this time" and then click "Create New Course."

2. \* **EdX Employee Required** \* Create the new course run using the following guidelines.

  
  \a. The course start and end dates **MUST** match the original course's start and end dates. 
  
  \b. The **Pacing** of the course should match the original course. 
  
  \c. For the **Enrollment Track**, select "Audit only." 

3. \* **Staff User or EdX Employee Required** \* After the shadow course is created, go into the Studio instance of the course and in Settings -> Advanced Settings, ensure **Course Visibility In Catalog** is "none". This ensures the shadow course cannot be found on edx.org and is not searchable.

4. \* **EdX Employee Required** \* To hide the shadow course on the dashboard in LMS, go into `Optimizely`_ and click on the experiment "Hide Review Courses." In the "Variations" tab, click on the variation "Hide Review Courses." On the left hand panel, click the button labelled "Custom JavaScript" and add in the review course to the custom JS in the variable "review_course_ids." The format it should follow is 

  ::

    "course-v1\\:ORGx\\+5\\.555x_review\\+1T2018"

.. _Optimizely: https://app.optimizely.com/v2/projects/1743970571

5. \* **EdX Employee Required** \* Create a Pull Request in `XBlock Review`_ that adds the original course key to SHOW_PROBLEMS or SHOW_VERTICAL as applicable to the course and a mapping of the original course to the shadow course in REVIEW_COURSE_MAPPING and ENROLLMENT_COURSE_MAPPING into **review/configuration.py**. In the same PR, update the version number in **setup.py**. Once the PR is merged, have an edX employee click on the `releases tab`_ and then click "Draft a new release." Under the tag version, write in the version from the PR in the **setup.py** file and give a title that gives a short description of the change made in the PR (e.g. "Adding in 5.555 to Review XBlock"). Make sure the new version is pushed to PyPI and then submit a Pull Request to `edX Platform`_ changing the version number for xblock-review in the requirements directory. Use this `search`_ to find where it is located in the repository. Ensure the Review XBlock version number is the same as the version you pushed to PyPI. An example of the change is below.

  ::

    Search for xblock-review on GitHub using the following `search`_ and update the version to match what you pushed to PyPI: 
    ...
    -xblock-review==1.1.3
    +xblock-review==1.1.4
    ...

.. _XBlock Review: https://github.com/edx/xblock-review
.. _releases tab: https://github.com/edx/xblock-review/releases
.. _edX Platform: https://github.com/edx/edx-platform
.. _search: https://github.com/edx/edx-platform/search?utf8=%E2%9C%93&q=xblock-review&type=

6. In Studio, click on "Tools" in the header and then select "Export" to bring you to the Course Export page. Click on the "Export Course Content" button and after it finishes, click the "Download Exported Course" button. This will download a file with ".tar.gz" at the end of it. 

Use the following steps based on whether you work in Studio or OLX (Open Learning XML).

If you work in **Studio** to develop your courses:

7. Go to your shadow course in Studio and click on "Tools" in the header and then select "Import" to bring you to the Course Import page. Click on the "Choose a File to Import" button and select the ".tar.gz" file from step 5. Then click "Replace my course with the selected file" and after it finishes, click the "View Updated Outline" button. You should now be able to see a replica of your actual course.

8. Go to Settings -> Advanced Settings and

  \a. Change **Course Display Name** to the name specified in step 1.
  
  \b. Ensure **Course Number Display String** is equal to "". This will make the Course Number display as it was created in step 1 with the "_review" at the end.
  
  \c. Ensure **Course Visibility In Catalog** is "none". This ensures the shadow course cannot be found on edx.org and is not searchable.
  
  \d. Save your changes.

9. For every subsection that includes problems, click on the "Configure" gear to the right of the title change the "Grade as:" setting to "Ungraded" and if a "Due Date" is shown, delete it. This ensures the learners know the problems they see in the Review XBlock are ungraded and by removing the Due Date, they will still be eligible problems to show a learner for review even after they are due in the actual course.

10. Next we want to enable learners to be able to attempt problems as many times as they would like when they are reviewing. Go to each problem in your course and click on the "EDIT" button and then the "Settings" button in the top right of the pop-up. Delete any number in the **Maximum Attempts** and the **Problem Weight** fields. Additionally, ensure **Show Answer** is set to "attempted" so learners can see the answer to the problem within the Review XBlock.

Now you're done setting up the shadow course for using the Review XBlock.

If you work in **OLX** to develop your courses:

7. Open the tar file for editing.

8. To remove problem weight, max attempts, graded, discussion, due date, and change showanswer to "attempted", copy the following content that is between the parentheses (e.g. **(copy_me)**). **Note:** The following steps are all using **regular expressions** to find specific substrings in the course. If you are not using a regular expression based find/replace tool, modify the strings below to have the desired effect:

  \a. Find/replace all occurrences of (\\ max_attempts="[0-9]*") with nothing (so it is deleted) and ("max_attempts":\\ [0-9]*,) with nothing
  
  \b. Find/replace all occurrences of (\\ attempts="[0-9]*") with nothing (so it is deleted) and ("attempts":\\ [0-9]*,) with nothing
  
  \c. Find/replace all occurrences of (\\ weight="[0-9]+\\.[0-9]*") with nothing (so it is deleted)
  
  \d. Find/replace all occurrences of (\\ graded="true") with nothing (so it is deleted) and ("graded": true,) with nothing 
  
  \e. Find/replace all occurrences of (\\ due="&quot;[0-9\\-T:\\+]+&quot;") with nothing (so it is deleted)
  
  \f. Find/replace all occurrences of (\\ \\ <discussion.*\\n) with nothing (so it is deleted)
  
  \g. Find/replace all occurrences of (showanswer="always"\|showanswer="answered"\|showanswer="closed"\|showanswer="finished"\|showanswer="past_due"\|showanswer="correct_or_past_due"\|showanswer="never") with (showanswer="attempted") and ("showanswer": "always"\|"showanswer": "answered"\|"showanswer": "closed"\|"showanswer": "finished"\|"showanswer": "past_due"\|"showanswer": "correct_or_past_due"\|"showanswer": "never") with ("showanswer": "attempted")

9. Change display_coursenumber and display_name from the original values to the values chosen in step 1 in your **policy.json** file so it doesn’t overwrite the review course name

10. Add ("catalog_visibility": "none",) in your **policy.json** file to prevent it from being found on the marketing site)

11. Review through your **policy.json** file for anything that contradicts any of the above steps. For example, this could be finding a line that states ``number: 5.555x`` instead of ``number: 5.555x_review``.

12. Compress the course folder using the command: tar -czvf [name_of_tar_file].tar.gz [name_of_folder_to_compress]

  \a. Ex: ``tar -czvf name_of_file.tar.gz Path/to/folder/to/compress/``

13. Go to your shadow course in Studio and click on "Tools" in the header and then select "Import" to bring you to the Course Import page. Click on the "Choose a File to Import" button and select the newly created tar file from step 12. Then click "Replace my course with the selected file" and after it finishes, click the "View Updated Outline" button. You should now be able to see the final version of the shadow course.

Adding the Review XBlock to your course
---------------------------------------

Process if using **Studio** to develop your course:

1. In Settings -> Advanced Settings, ensure **Add Unsupported Problems and Tools** is "true".

2. In Settings -> Advanced Settings, add "review" to the **Advanced Module List**.

3. Create a subsection where you want to add the Review XBlock.

4. Create a unit inside the new subsection

5. Inside the new unit, select **Advanced** under **Add New Component**.

6. Select **Review**.

7. Repeat steps 3 - 6 as desired.

Process if using **OLX** (Open Learning XML) to develop your course:

1. Add "review" to **advanced modules** in your **policy.json** file. 

  \a. An example path would be policies/course/policy.json
  
  \b. An example of what the **policy.json** file would look like afterwards:

    ::

      {
        "course/course": {
          "advanced_modules": [
            "review",
          ],
          ...

2. Add sequentials into chapter xml.

  \a. An example of what the chapter xml would look like afterwards:

    ::
    
      <sequential url_name="W2_review_sequential"/>

3. Create sequentials for each vertical (sequential filename must match url_name in chapter from above).

  \a. Assuming url_name was "W2_review_sequential" in the chapter xml (as above), file name for sequential should be "W2_review_sequential.xml"
  
  \b. An example of what the sequential xml would look like afterwards:
    
    ::

      W2_review_sequential.xml:
        <sequential display_name="W2 Review Subsection">
            <vertical url_name="W2_review_unit"/>
        </sequential>

4. Create verticals for each review unit (vertical filename must match url_name in sequential from above).

  \a. Assuming url_name was "W2_review_unit" in the sequential xml (as above), file name for vertical should be "W2_review_unit.xml"
  
  \b. An example of what the vertical xml would look like afterwards:

    ::

       W2_review_unit.xml:
        <vertical display_name="W2 Review Unit">
            <review url_name="W2_actual_review_block" xblock-family="xblock.v1"/>
        </vertical>
