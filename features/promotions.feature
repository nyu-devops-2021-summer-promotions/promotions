Feature: The promotion service back-end
    As a Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my promotion

    Background:
        Given the following promotions
            | title          | promotion_type   | start_date | end_date   | active |
            | Christmas Sale | buy 1 get 2      | 2021-07-01 | 2022-07-01 | true   |
            | New Product    | 10%OFF           | 2021-01-01 | 2022-01-01 | false  |
            | Black Friday   | 20%OFF           | 2021-12-01 | 2022-12-01 | true   |
            | Summer Sale    | buy 1 get 1 free | 2021-11-01 | 2022-11-01 | false  |


    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Promotion RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create a Promotion
        When I visit the "Home Page"
        And I set the "title" to "Christmas Sale"
        And I set the "promotion_type" to "buy 1 get 2"
        And I set the "start_date" to "08/12/2021"
        And I set the "end_date" to "08/31/2021"
        And I select "False" in the "Active" dropdown
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "Title" field should be empty
        And the "promotion_type" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see "Christmas Sale" in the "title" field
        And I should see "buy 1 get 2" in the "promotion_type" field
        And I should see "2021-08-12" in the "start_date" field
        And I should see "2021-08-31" in the "end_date" field
        And I should see "False" in the "Active" dropdown


    Scenario: List all Promotions
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see "New Product" in the results
        And I should see "Christmas Sale" in the results
        And I should see "Black Friday" in the results
        And I should see "Summer Sale" in the results
        And I should not see "Winter Sale" in the results

    Scenario: Read a promotion
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        When I press the "Retrieve" button
        Then I should see "Christmas Sale" in the "title" field
        And I should see "buy 1 get 2" in the "promotion_type" field
        And I should see "2021-07-01" in the "start_date" field
        And I should see "2022-07-01" in the "end_date" field
        And I should see "True" in the "Active" dropdown

    Scenario: Query a Promotion
        When I visit the "Home Page"
        And I set the "promotion_type" to "10%OFF"
        And I press the "Search" button
        Then I should see "New Product" in the results
        And I should not see "Christmas Sale" in the results
        And I should not see "Black Friday" in the results
        And I should not see "Summer Sale" in the results
        When I press the "Clear" button
        And I set the "title" to "Black Friday"
        And I press the "Search" button
        Then I should see "20%OFF" in the results
        And I should not see "10%OFF" in the results
        And I should not see "buy 1 get 1 free" in the results
        And I should not see "buy 1 get 2" in the results
        When I press the "Clear" button
        And I set the "end_date" to "11/01/2022"
        And I press the "Search" button
        Then I should see "Summer Sale" in the results
        And I should not see "Christmas Sale" in the results
        And I should not see "Black Friday" in the results
        And I should not see "New Product" in the results
        When I press the "Clear" button
        And I select "True" in the "active" dropdown
        And I press the "Search" button
        Then I should see "Christmas Sale" in the results
        And I should see "Black Friday" in the results
        And I should not see "Summer Sale" in the results
        And I should not see "New Product" in the results

    Scenario: Update a Promotion
        When I visit the "Home Page"
        And I set the "title" to "Black Friday"
        And I press the "Search" button
        Then I should see "Black Friday" in the "title" field
        And I should see "20%OFF" in the "promotion_type" field
        When I change "title" to "Winter Sale"
        And I press the "Update" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see "Winter Sale" in the "title" field
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see "Winter Sale" in the results
        Then I should not see "Black Friday" in the results

    Scenario: Delete a Promotion
        When I visit the "Home Page"
        And I set the "title" to "Black Friday"
        And I press the "Search" button
        Then I should see "Black Friday" in the "title" field
        And I should see "20%OFF" in the "promotion_type" field
        When I press the "Delete" button
        Then I should see the message "Promotion has been Deleted!"
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see "Christmas Sale" in the results
        Then I should not see "Black Friday" in the results

    Scenario: Activate a Promotion
        When I visit the "Home Page"
        And I set the "title" to "New Product"
        And I press the "Search" button
        Then I should see the message "Success"
        Then I should see "New Product" in the results
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        When I press the "Retrieve" button
        Then I should see "New Product" in the "title" field
        And I should see "10%OFF" in the "promotion_type" field
        And I should see "2021-01-01" in the "start_date" field
        And I should see "2022-01-01" in the "end_date" field
        And I should see "False" in the "Active" dropdown
        When I press the "Activate" button
        Then I should see the message "Promotion has been activated!"
        And I should see "True" in the "Active" dropdown

    Scenario: Deactivate a Promotion
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        Then I should see "Christmas Sale" in the results
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        When I press the "Retrieve" button
        Then I should see "Christmas Sale" in the "title" field
        And I should see "buy 1 get 2" in the "promotion_type" field
        And I should see "2021-07-01" in the "start_date" field
        And I should see "2022-07-01" in the "end_date" field
        And I should see "True" in the "Active" dropdown
        When I press the "Deactivate" button
        Then I should see the message "Promotion has been deactivated!"
        And I should see "False" in the "Active" dropdown


