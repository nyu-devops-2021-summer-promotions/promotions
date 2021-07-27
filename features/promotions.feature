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

    Scenario: List all Promotions

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

    Scenario: Search all 10%OFF

    Scenario: Update a Promotion

    Scenario: Delete a Promotion

    Scenario: Activate a Promotion

    Scenario: Deactivate a Promotion


