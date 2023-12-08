Import-Module ActiveDirectory

function Get-RandomString {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    $length = 27
    $randomString = -join ((1..$length) | ForEach-Object { Get-Random -Maximum $characters.Length | ForEach-Object { $characters[$_]} })
    return $randomString
}

Get-ADUser -Filter * -Properties Description | ForEach-Object {
    $newDescription = Get-RandomString
    Set-ADUser $_ -Description $newDescription
    Write-Host "Updated user $($_.SamAccountName) with new description: $newDescription"
}
